#!/bin/bash 

# Create a cron file on the fly based on docker environment variables,
# Then immediately pipe it to crontab
echo "$CRON_EXPR /usr/sbin/logrotate $LOGROTATE_OPTIONS $LOGROTATE_CONF" '> /proc/$(cat /var/run/crond.pid)/fd/1 2>&1' | crontab - 

# Start cron in non-daemon (foreground) mode
crond -n
