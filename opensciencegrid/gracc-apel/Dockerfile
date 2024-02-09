ARG BASE_OS=el9
ARG BASE_OSG_SERIES=3.6
ARG BASE_YUM_REPO=release

FROM hub.opensciencegrid.org/opensciencegrid/software-base:$BASE_OSG_SERIES-$BASE_OS-$BASE_YUM_REPO

# Reinitiate vars that have gone out of scope
ARG BASE_OS

# install dependencies
RUN yum -y install python3 python3-pip && \
  pip3 install elasticsearch-dsl requests && \
  pip3 install argo-ams-library
RUN yum -y install http://rpm-repo.argo.grnet.gr/ARGO/devel/centos7/python-argo-ams-library-0.5.5-20210415071520.ff0c536.$BASE_OS.noarch.rpm

RUN yum -y install python-dirq

# install ca-policy-egi-core
RUN yum -y remove osg-ca-certs
RUN curl -so /etc/yum.repos.d/EGI-trustanchors.repo https://repository.egi.eu/sw/production/cas/1/current/repo-files/egi-trustanchors.repo && \
  yum -y install ca-policy-egi-core


RUN yum -y install https://github.com/apel/ssm/releases/download/3.2.1-1/apel-ssm-3.2.1-1.$BASE_OS.noarch.rpm  && \
  mkdir /etc/grid-security/apel && \
  mkdir -p /var/spool/apel/outgoing/12345678 && \
  { fetch-crl -p10 -T10 || :; }

COPY apel_report.py normal_hepspec docker-run.sh /usr/libexec/apel/
COPY sender.cfg /etc/apel/

ENTRYPOINT ["/usr/libexec/apel/docker-run.sh"]
