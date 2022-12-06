ARG BASE_YUM_REPO=release
ARG BASE_OSG_SERIES=3.6

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-el8-$BASE_YUM_REPO

LABEL maintainer OSG Software <help@opensciencegrid.org>

RUN yum -y install \
             vim && \
    yum -y clean all

ADD mailchimp-sync /srv/mailchimp-sync

ENTRYPOINT ["/srv/mailchimp-sync/runme.sh"]


