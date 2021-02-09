FROM opensciencegrid/software-base:fresh

LABEL maintainer OSG Software <help@opensciencegrid.org>

# Default root dir
ENV XC_ROOTDIR /xrootd-standalone

# Create the xrootd user with a fixed GID/UID
RUN groupadd -o -g 10940 xrootd
RUN useradd -o -u 10940 -g 10940 -s /bin/sh xrootd

RUN yum update -y && \
    yum clean all && \
    rm -rf /var/cache/yum/*

RUN yum install -y osg-xrootd-standalone --enablerepo=osg-upcoming-testing && \
    yum clean all && \
    rm -rf /var/cache/yum/*

ADD supervisord.d/* /etc/supervisord.d/
ADD image-config.d/* /etc/osg/image-config.d/
ADD xrootd/* /etc/xrootd/config.d/
