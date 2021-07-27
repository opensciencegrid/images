ARG BASE_YUM_REPO=release

FROM opensciencegrid/software-base:3.5-el7-$BASE_YUM_REPO

LABEL maintainer OSG Software <help@opensciencegrid.org>

ARG BASE_YUM_REPO=release

RUN yum update -y && \
    yum clean all && \
    rm -rf /var/cache/yum/*

RUN yum install -y oidc-agent && \
    yum clean all && \
    rm -rf /var/cache/yum/*
    
COPY runme.sh /usr/local/bin
COPY oidc-gen.sh /usr/local/bin
COPY oidc-add.sh /usr/local/bin
COPY oidc-agent.sh /usr/local/bin
COPY oidc-keychain.sh /usr/local/bin
COPY oidc-token.sh /usr/local/bin

ENTRYPOINT ["/usr/local/bin/runme.sh"]
