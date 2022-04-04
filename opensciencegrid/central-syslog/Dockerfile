ARG BASE_OSG_SERIES=3.6
ARG BASE_YUM_REPO=release

FROM hub.opensciencegrid.org/opensciencegrid/software-base:$BASE_OSG_SERIES-el8-$BASE_YUM_REPO

LABEL maintainer OSG Software <support@opensciencegrid.org>

RUN yum -y install rsyslog \
                   rsyslog-gnutls \
    && mkdir /data/

COPY etc /etc
RUN mv /etc/cron.daily/logrotate /etc/cron.hourly/logrotate
