ARG BASE_YUM_REPO=release

FROM opensciencegrid/software-base:$BASE_YUM_REPO

LABEL maintainer OSG Software <help@opensciencegrid.org>

ARG BASE_YUM_REPO=release

# Default root dir
ENV XC_ROOTDIR /xrootd-standalone

# Create the xrootd user with a fixed GID/UID
RUN groupadd -o -g 10940 xrootd
RUN useradd -o -u 10940 -g 10940 -s /bin/sh xrootd

RUN yum update -y && \
    yum clean all && \
    rm -rf /var/cache/yum/*

RUN if [[ $BASE_YUM_REPO = release ]]; then \
       yumrepo=osg-upcoming; else \
       yumrepo=osg-upcoming-$BASE_YUM_REPO; fi && \
    yum install -y --enablerepo=$yumrepo && \
    yum clean all && \
    rm -rf /var/cache/yum/*

ADD supervisord.d/* /etc/supervisord.d/
ADD image-config.d/* /etc/osg/image-config.d/
ADD xrootd/* /etc/xrootd/config.d/
