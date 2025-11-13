#!/bin/bash
# shellcheck disable=2016

# Create a cron file on the fly based on docker environment variables,

# We must start the cron job itself as root so we can send its output to
# the container's stdout/err, but then drop privileges to run the
# actual script.

echo "${CRON_EXPR?} root cd /ospool/images-scripts && /usr/sbin/runuser -u images -- timeout -k 60s ${TIMEOUT?} ./update.py /ospool/images/v2" '> /proc/1/fd/1 2>&1' > /etc/cron.d/update.cron

# Start cron in non-daemon (foreground) mode
echo >&2 "Starting cron"
exec crond -n
echo >&2 "Exec failed!"
exit 255
