ARG BASE_OS=el9
ARG BASE_OSG_SERIES=23
ARG BASE_YUM_REPO=release

FROM hub.opensciencegrid.org/opensciencegrid/software-base:$BASE_OSG_SERIES-$BASE_OS-$BASE_YUM_REPO

# Reinitiate vars that have gone out of scope
ARG BASE_OS

# install dependencies
RUN    dnf install -y \
         python3 \
         python3-dirq \
         python3-pip \
         https://github.com/apel/ssm/releases/download/3.4.0-1/apel-ssm-3.4.0-1.$BASE_OS.noarch.rpm \
# ARGO AMS
    && dnf install -y \
         --repofrompath argo,http://rpm-repo.argo.grnet.gr/ARGO/prod/rocky9/ \
         --nogpgcheck \
         python3-argo-ams-library \
# EGI CA certificates
    && dnf config-manager --add-repo \
         https://repository.egi.eu/sw/production/cas/1/current/repo-files/egi-trustanchors.repo \
    && dnf swap -y osg-ca-certs ca-policy-egi-core \
    && dnf clean all

RUN    pip3 install --no-cache-dir \
         opensearch-py \
         requests

# EPEL for EL9 ships python3-daemon-2.3.2-1.el9.noarch
# It uses excessive memory when nofile ulimit is high, fixed in >= v3.0.0
# https://pagure.io/python-daemon/issue/72
# TODO: Revert after EPEL package is updated
RUN    pip3 install --no-cache-dir --upgrade \
         python-daemon

RUN    mkdir /etc/grid-security/apel \
    && mkdir -p /var/spool/apel/outgoing/12345678

COPY apel_report.py normal_hepspec docker-run.sh /usr/libexec/apel/
COPY sender.cfg /etc/apel/

ENTRYPOINT ["/usr/libexec/apel/docker-run.sh"]
