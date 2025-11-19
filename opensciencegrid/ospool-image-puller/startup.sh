#!/bin/bash
# shellcheck disable=2016

# Create the 'images' user, if it doesn't already exist.

getent passwd images >/dev/null || useradd --home-dir /var/home/images -u "${IMAGES_UID?}" images
install -o images -d /var/home/images

TARGET_DIR=/ospool/images/v2
install -o images -d "${TARGET_DIR}"


# Create a cron file on the fly based on docker environment variables,

# We must start the cron job itself as root so we can send its output to
# the container's stdout/err, but then drop privileges to run the
# actual script.

echo "${CRON_EXPR?} root cd /ospool/images-scripts && /usr/sbin/runuser -u images -- timeout -k 60s ${TIMEOUT?} ./update.py ${TARGET_DIR}" '> /proc/1/fd/1 2>&1' > /etc/cron.d/update.cron

# Start cron in non-daemon (foreground) mode
echo >&2 "Starting cron"
exec crond -n
echo >&2 "Exec failed!"
exit 255
