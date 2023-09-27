ARG BASE_YUM_REPO=release
ARG BASE_OSG_SERIES=3.6
ARG BASE_OS=el9

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-$BASE_OS-$BASE_YUM_REPO

LABEL maintainer OSG Software <help@opensciencegrid.org>

ARG BASE_YUM_REPO=release

# Default root dir
ENV XC_ROOTDIR /xrootd-standalone

# Create the xrootd user with a fixed GID/UID
RUN groupadd -o -g 10940 xrootd
RUN useradd -o -u 10940 -g 10940 -s /bin/sh xrootd

# Create an empty macaroon-secret now so RPM installs won't create one, adding it to a layer.
RUN mkdir -p /etc/xrootd && touch /etc/xrootd/macaroon-secret

RUN yum install -y osg-xrootd-standalone && \
    yum clean all && \
    rm -rf /var/cache/yum/*

ADD supervisord.d/* /etc/supervisord.d/
ADD image-config.d/* /etc/osg/image-config.d/
ADD xrootd/* /etc/xrootd/config.d/

RUN rm -f /etc/xrootd/macaroon-secret
