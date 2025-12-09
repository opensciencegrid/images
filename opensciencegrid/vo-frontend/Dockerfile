ARG BASE_YUM_REPO=release
ARG BASE_OSG_SERIES=24
ARG BASE_OS=el9

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-$BASE_OS-$BASE_YUM_REPO

LABEL maintainer="OSG Software <support@osg-htc.org>"

# Create the frontend user with a fixed GID/UID
# This is important so that we can use the same IDs in the persistent volume used for
# the web-area
RUN groupadd -o -g 993 frontend
RUN useradd -o -u 996 -g 993 -s /bin/sh frontend

# for developement, grab gwms from upcoming
RUN yum --disablerepo=osg-upcoming -y install \
      git \
      glideinwms-vofrontend-standalone \
      jq \
      patch \
      python3-scitokens \
      rsyslog \
      rsyslog-gnutls \
      vim \
      vo-client && \
    if [[ $BASE_YUM_REPO = development ]]; then \
      yum -y --enablerepo=osg-upcoming-development upgrade glideinwms-vofrontend-standalone; \
    fi && \
    yum -y clean all

# clean log dirs
RUN rm -rf /var/log/gwms-frontend/*

# GWMS brings in mod_ssl, which now drops a default ssl config in
# /etc/httpd/conf.d/ssl.conf which prevents the frontend httpd from
# starting up. We do not need this file, as ssl is handled by k8s
# ingress.
RUN rm -f /etc/httpd/conf.d/ssl.conf

# patch gwms (but only for certain versions)
ADD patches /opt/gwms-patches
RUN VERSION=$(rpm -qa | grep glideinwms-libs | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+') && \
    if [ -e /opt/gwms-patches/$VERSION.sh ]; then \
        /opt/gwms-patches/$VERSION.sh; \
    else \
        echo "No patch for version $VERSION"; \
    fi

ADD healthy.sh /healthy.sh

ADD image-config.d/*    /etc/osg/image-config.d/
ADD cron.d/*            /etc/cron.d/
ADD supervisor.d/*      /etc/supervisord.d/
ADD condor.d/*          /etc/condor/config.d/


