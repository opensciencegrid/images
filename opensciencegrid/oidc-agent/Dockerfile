FROM opensciencegrid/software-base:fresh

LABEL maintainer OSG Software <help@opensciencegrid.org>

RUN yum update -y && \
    yum clean all && \
    rm -rf /var/cache/yum/*

RUN yum install -y oidc-agent --enablerepo=osg-testing && \
    yum clean all && \
    rm -rf /var/cache/yum/*
    
RUN eval ssh-agent

ENTRYPOINT ["oidc-agent"]
