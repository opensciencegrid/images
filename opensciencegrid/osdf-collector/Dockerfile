ARG BASE_OSG_SERIES=3.6
ARG BASE_YUM_REPO=testing

FROM opensciencegrid/software-base:${BASE_OSG_SERIES}-el8-${BASE_YUM_REPO}
LABEL maintainer "OSG Software <help@opensciencegrid.org>"

RUN yum install -y condor rsyslog \
    && yum clean all \
    && rm -rf /var/cache/yum/

COPY etc/ /etc/
