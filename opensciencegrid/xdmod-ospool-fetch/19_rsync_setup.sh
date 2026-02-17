#!/bin/bash

# Fail if variables are unset
set -u

RSYNC_KEYS_CONFIG_DIR=${RSYNC_KEYS_CONFIG_DIR:-/mnt/ssh-keys-config}

mode="${1:-init}"
if [[ "$mode" != "cron" ]]; then
    mkdir -p /root/.ssh
    chmod 700 /root/.ssh
fi

# Always (re)install the ssh key when this script runs
pushd $RSYNC_KEYS_CONFIG_DIR
for FILE in *; do
    echo "Installing ssh key/config $FILE to /root/.ssh/$FILE"
    install -o root -g root -m 0600 $FILE /root/.ssh/$FILE
done
popd

if [[ "$mode" != "cron" ]]; then
    # Periodically re-install the ssh key every 5 minutes around rsync time
    cat >/etc/cron.d/rsync-setup.cron <<EOF
SHELL=/bin/bash
PATH=/usr/sbin:/usr/bin:/sbin:/bin
RSYNC_KEYS_CONFIG_DIR=${RSYNC_KEYS_CONFIG_DIR}
*/5 ${RSYNC_CRON_HOUR:-8} * * * root /etc/osg/image-config.d/19_rsync_setup.sh cron >>/var/log/rsync-setup.log 2>&1
EOF

    # Run the rsync once per day, time in UTC
    cat >/etc/cron.d/rsync-ospool-logs.cron <<EOF
SHELL=/bin/bash
PATH=/usr/sbin:/usr/bin:/sbin:/bin
${RSYNC_CRON_MINUTE:-30} ${RSYNC_CRON_HOUR:-8} * * * root rsync -ave --delete ssh ${RSYNC_SOURCE} ${RSYNC_TARGET} >>/var/log/rsync-ospool-logs.log 2>&1
EOF

    # Run the rsync now if RUN_RSYNC_NOW is defined
    if [[ "x${RUN_RSYNC_NOW}" != "x" ]]; then
        echo "Running rsync on startup from ${RSYNC_SOURCE} to ${RSYNC_TARGET}"
        rsync -ave ssh ${RSYNC_SOURCE} ${RSYNC_TARGET} >>/var/log/rsync-ospool-logs.log 2>&1
    fi
fi
