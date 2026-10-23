#!/bin/bash
#
# Checks a built provisioner image. Usage:
#
#   tests/image.sh <image>        (from the provisioner directory)
#
# Needs docker. The startup check makes real (read-only) queries to the OSPool collector and
# to IceCube's schedd (tests/sample_osg_provisioner.conf), so it needs network access; without
# it the loop still starts, but logs query failures.
#
set -u
IMG=${1:?usage: $0 <image>}
TESTS=$(cd "$(dirname "$0")" && pwd)
# inside the nrp-provisioner repo, the unit tests also check the namespace configs in k8s/
K8S=$(cd "$TESTS/../../k8s" 2>/dev/null && pwd)
PLATFORM=${PLATFORM:-linux/amd64}
fails=0
pass() { echo "PASS  $*"; }
fail() { echo "FAIL  $*"; fails=$((fails+1)); }
run() { docker run --rm --platform "$PLATFORM" "$@"; }

echo "== $IMG"
run --entrypoint bash "$IMG" -c 'grep PRETTY_NAME /etc/os-release; python3 --version; rpm -q condor python3-condor osg-ca-certs; python3 -c "import kubernetes; print(\"kubernetes\", kubernetes.__version__)"' | sed 's/^/      /'

# 1) unit tests, inside the image (they need the htcondor2 bindings and the kubernetes client)
out=$(run -v "$TESTS:/t:ro" ${K8S:+-v "$K8S:/k8s:ro"} --entrypoint bash "$IMG" -c \
  'mkdir -p /tmp/w/p && ln -s /opt/provisioner/src /tmp/w/p/src && cp -r /t /tmp/w/p/tests && { [ ! -d /k8s ] || ln -s /k8s /tmp/w/k8s; } && cd /tmp/w/p && python3 -B -m unittest discover -s tests 2>&1')
echo "$out" | grep -q "^OK" && pass "unit tests: $(echo "$out" | grep '^Ran')" || { fail "unit tests"; echo "$out" | tail -20; }
echo "$out" | grep -q "skipped" && fail "unit tests were skipped inside the image: $(echo "$out" | grep -o 'skipped=[0-9]*')"

# 2) the provisioner user's home has the shell profile that 'su -l' needs
home=$(run --entrypoint bash "$IMG" -c 'ls -A /home/provisioner')
echo "$home" | grep -qx ".bash_profile" && pass "home has .bash_profile" || fail "home has no .bash_profile (useradd skipped /etc/skel?)"

# 3) the setup scripts' environment reaches the provisioner's login shell
envout=$(run -e HTCONDOR_QUERY_INSECURE=yes -e KUBERNETES_SERVICE_HOST=192.0.2.1 -e KUBERNETES_SERVICE_PORT=443 -e K8S_NAMESPACE=osg-test --entrypoint bash "$IMG" -c \
  'mkdir -p /etc/condor/tokens.d && touch /etc/condor/tokens.d/test.token; /opt/provisioner/setup_k8s_creds.sh; /opt/provisioner/setup_htcondor_creds.sh; su -l provisioner -c "echo \$KUBERNETES_SERVICE_HOST \$KUBERNETES_SERVICE_PORT \$K8S_NAMESPACE \$_CONDOR_SEC_CLIENT_AUTHENTICATION; ls ~/.condor/tokens.d"')
[ "$(echo "$envout" | head -1)" = "192.0.2.1 443 osg-test OPTIONAL" ] && pass "environment reaches 'su -l provisioner'" || fail "environment did not reach the provisioner: $envout"
echo "$envout" | grep -qx "test.token" && pass "tokens copied to the provisioner user" || fail "tokens not copied"

# 4) startup with a fake service account: must get into the provisioning loop
sa=$(mktemp -d); echo fake > "$sa/token"; echo osg-icecube > "$sa/namespace"
printf -- '-----BEGIN CERTIFICATE-----\nZmFrZQ==\n-----END CERTIFICATE-----\n' > "$sa/ca.crt"
chmod 755 "$sa"; chmod 644 "$sa"/*  # mktemp -d is 0700; the provisioner user in the container must read it
start=$(run -e CONDOR_HOST=cm-1.ospool.osg-htc.org,cm-2.ospool.osg-htc.org -e K8S_NAMESPACE=osg-icecube -e CVMFS_MOUNTS=icecube,singularity \
  -e HTCONDOR_QUERY_INSECURE=yes -e KUBERNETES_SERVICE_HOST=127.0.0.1 -e KUBERNETES_SERVICE_PORT=6443 \
  -v "$sa:/var/run/secrets/kubernetes.io/serviceaccount:ro" -v "$TESTS/sample_osg_provisioner.conf:/cfg/osg_provisioner.conf:ro" \
  --entrypoint bash "$IMG" -c '
    mkdir -p /etc/condor/tokens.d && touch /etc/condor/tokens.d/none.token
    cp /cfg/osg_provisioner.conf /home/provisioner/ && chown provisioner /home/provisioner/osg_provisioner.conf
    /opt/provisioner/provisioner_startup.sh > /tmp/out 2>&1 &
    for i in $(seq 1 90); do grep -q "Iteration started" /tmp/out 2>/dev/null && break; sleep 1; done
    sleep 3; cat /tmp/out')
rm -rf "$sa"
echo "$start" | grep -q "Iteration started" && pass "startup reaches the provisioning loop (and logs it to stdout)" || { fail "startup did not reach the loop"; echo "$start" | tail -20 | sed 's/^/      /'; }
echo "$start" | grep -q "Traceback" && { fail "traceback during startup"; echo "$start" | grep -A8 Traceback | sed 's/^/      /'; } || pass "no traceback during startup"
echo "$start" | grep -q "FutureWarning\|DeprecationWarning" && fail "deprecation warnings during startup" || pass "no deprecation warnings"
echo "$start" | grep -q "Failed to query HTCondor schedd" && echo "NOTE  a schedd query failed (network, CA bundle or schedd policy?):" && echo "$start" | grep "Failed to query HTCondor schedd" | head -3 | sed 's/^/      /'

echo; [ $fails -eq 0 ] && echo "ALL PASSED" || echo "$fails FAILED"
exit $fails
