# Specify the opensciencegrid/software-base image tag
ARG BASE_OSG_SERIES=3.5
ARG BASE_YUM_REPO=release

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-el7-$BASE_YUM_REPO

LABEL maintainer OSG Software <help@opensciencegrid.org>

ARG BASE_YUM_REPO=release

RUN yum update -y && \
    yum install -y oidc-agent && \
    yum clean all && \
    rm -rf /var/cache/yum/*
    
COPY bin/* /usr/local/bin

ENTRYPOINT ["/usr/local/bin/runme.sh"]
