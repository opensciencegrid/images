#!/bin/bash

fail () {
    ret=$1
    shift
    echo >&2 "create-config.sh: $*"
    sleep 30
    exit "$ret"
}

set -u
[[ $KOJI_HUB ]] || fail 2 KOJI_HUB not provided
[[ $KOJID_USER ]] || fail 2 KOJID_USER not provided
[[ -f $KOJID_CERTKEY ]] || fail 3 "KOJID_CERTKEY $KOJID_CERTKEY missing or not a file"
[[ -d $KOJID_WORKDIR ]] || fail 4 "KOJID_WORKDIR $KOJID_WORKDIR missing or not a directory"

commonName=$(openssl x509 -in "$KOJID_CERTKEY" -noout -subject -nameopt multiline | awk -F' = ' '/commonName/ {print $2;exit}')
if [[ $commonName != "$KOJID_USER" ]]; then
    fail 5 "KOJID_CERTKEY commonName $commonName does not match KOJID_USER $KOJID_USER"
fi

tmp_conf=$(mktemp -t kojid-conf-XXXXXX)
trap 'rm -f $tmp_conf' ERR EXIT

cat > "$tmp_conf" <<TLDR
[kojid]
user = $KOJID_USER
maxjobs = $KOJID_MAXJOBS
minspace = $KOJID_MINSPACE
rpmbuild_timeout = $KOJID_RPMBUILD_TIMEOUT

server = https://${KOJI_HUB}/kojihub
topurl = https://${KOJI_HUB}/kojifiles

workdir = $KOJID_WORKDIR

allowed_scms=
    vdt.cs.wisc.edu:/svn/native/*:no:fetch-sources,.
    github.com:/unlhcc/hcc-packaging.git:no:fetch-sources,.
    github.com:/opensciencegrid/Software-Redhat.git:no:fetch-sources,.
    github.com:/CHTC/packaging.git:no:fetch-sources,.
    github.com:/osg-htc/software-packaging.git:no:fetch-sources,.

cert = $KOJID_CERTKEY
serverca = /etc/pki/tls/certs/ca-bundle.crt

TLDR

install -o root -g root -m 0644 "$tmp_conf" /etc/kojid/kojid.conf || fail 1 error placing kojid.conf

