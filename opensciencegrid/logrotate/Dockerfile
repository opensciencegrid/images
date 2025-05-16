FROM almalinux:9

LABEL maintainer OSG Software <help@osg-htc.org>

# Run Logrotate every five minutes
ENV CRON_EXPR="*/5 * * * *"
# Extra options to logrotate (if any)
ENV LOGROTATE_OPTIONS=
# File path(s) for LogRotate config files
ENV LOGROTATE_CONF="/etc/logrotate.d/*.logrotate"

RUN yum install -y crontabs \
                   cronie \
                   logrotate \
    && yum clean all

COPY startup.sh /bin/
CMD [ "/bin/startup.sh" ]
