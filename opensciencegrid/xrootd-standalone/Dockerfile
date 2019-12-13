FROM opensciencegrid/software-base:fresh

LABEL maintainer OSG Software <help@opensciencegrid.org>

RUN yum update -y && yum clean all && rm -rf /var/cache/yum/*

RUN yum install -y osg-xrootd-standalone --enablerepo=osg-development && yum clean all && rm -rf /var/cache/yum/*
