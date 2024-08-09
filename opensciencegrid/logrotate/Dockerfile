FROM almalinux:9

LABEL maintainer OSG Software <help@osg-htc.org>

# Run Logrotate once per hour
ENV CRON_EXPR="0 * * * *"
# Extra options to logrotate (if any)
ENV LOGROTATE_OPTIONS=
# File path(s) for LogRotate config files
ENV LOGROTATE_CONF="/etc/logrotate.d/*.logrotate"

RUN yum install -y crontabs \
                   cronie \
                   logrotate \
    && yum clean all

CMD [ "sh", "-c", "echo \"$CRON_EXPR /usr/sbin/logrotate $LOGROTATE_OPTIONS $LOGROTATE_CONF\" '> /proc/$(cat /var/run/crond.pid)/fd/1 2>&1' | crontab - && crond -n"]
