ARG BASE_YUM_REPO=release

FROM opensciencegrid/software-base:3.5-el7-$BASE_YUM_REPO

LABEL maintainer OSG Software <help@opensciencegrid.org>

ARG BASE_YUM_REPO=release

RUN yum update -y && \
    yum install -y oidc-agent && \
    yum clean all && \
    rm -rf /var/cache/yum/*
    
COPY bin/* /usr/local/bin

ENTRYPOINT ["/usr/local/bin/runme.sh"]
