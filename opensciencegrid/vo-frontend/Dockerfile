ARG BASE_YUM_REPO=release
ARG BASE_OSG_SERIES=3.6

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-el7-$BASE_YUM_REPO

LABEL maintainer OSG Software <help@opensciencegrid.org>

# Create the frontend user with a fixed GID/UID
# This is important so that we can use the same IDs in the persistent volume used for
# the web-area
RUN groupadd -o -g 993 frontend
RUN useradd -o -u 996 -g 993 -s /bin/sh frontend

RUN yum -y install \
      git \
      glideinwms-vofrontend-standalone \
      jq \
      patch \
      python3-scitokens \
      rsyslog \
      rsyslog-gnutls \
      vim \
      vo-client && \
    yum -y clean all

# clean log dirs
RUN rm -rf /var/log/gwms-frontend/*

# patch gwms (but only for certain versions)
ADD patches /opt/gwms-patches
#RUN if rpm -qa | grep glideinwms-libs-3.9.4; then /tmp/patch_gwms.sh; fi
RUN VERSION=$(rpm -qa | grep glideinwms-libs | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+') && \
    if [ -e /opt/gwms-patches/$VERSION.sh ]; then \
        /opt/gwms-patches/$VERSION.sh; \
    else \
        echo "No patch for version $VERSION"; \
    fi

ADD healthy.sh /healthy.sh
ADD frontend_scitoken_check_ces /usr/sbin/frontend_scitoken_check_ces
ADD frontend_scitoken_check_ces.cron /etc/cron.d/frontend_scitoken_check_ces.cron

ADD image-config.d/*    /etc/osg/image-config.d/
ADD cron.d/*            /etc/cron.d/
ADD supervisor.d/*      /etc/supervisord.d/
ADD condor.d/*          /etc/condor/config.d/

