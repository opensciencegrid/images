ARG BASE_YUM_REPO=release
ARG BASE_OSG_SERIES=3.6

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-el8-$BASE_YUM_REPO

LABEL maintainer OSG Software <help@opensciencegrid.org>

# Create the frontend user with a fixed GID/UID
# This is important so that we can use the same IDs in the persistent volume used for
# the web-area
RUN groupadd -o -g 993 frontend
RUN useradd -o -u 996 -g 993 -s /bin/sh frontend

RUN yum -y install \
    git \
    jq \
    rsyslog \
    rsyslog-gnutls \
    vo-client

# javascriptrrd - different location in OSG 3.5 and 3.6
RUN yum -y install --enablerepo=osg-testing \
           javascriptrrd \
    || \
    yum -y install --enablerepo=osg-minefield \
           javascriptrrd

# pull gwms from upcoming
RUN yum -y install --enablerepo=osg-upcoming \
           glideinwms-vofrontend-standalone \
    || \
    yum -y install --enablerepo=osg-development \
           glideinwms-vofrontend-standalone

ADD image-config.d/*    /etc/osg/image-config.d/
ADD cron.d/*            /etc/cron.d/
ADD supervisor.d/*      /etc/supervisord.d/
ADD condor.d/*          /etc/condor/config.d/

