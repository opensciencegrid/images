FROM almalinux:9

LABEL maintainer OSG Software <help@osg-htc.org>

RUN yum -y install python3 python3-requests && \
    yum -y clean all

ADD mailchimp-sync /srv/mailchimp-sync

CMD ["/srv/mailchimp-sync/runme.sh"]


