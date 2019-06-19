#!/bin/bash -e

cp /tmp/fts3-host-pems/hostcert.pem /etc/grid-security/
chmod 644 /etc/grid-security/hostcert.pem
chown root:root /etc/grid-security/hostcert.pem
cp /tmp/fts3-host-pems/hostkey.pem /etc/grid-security/
chmod 400 /etc/grid-security/hostkey.pem
chown root:root /etc/grid-security/hostkey.pem
cp /tmp/fts3-configs/fts3config /etc/fts3/fts3config
cp /tmp/fts3-configs/fts-msg-monitoring.conf /etc/fts3/fts-msg-monitoring.conf
mkdir -p /var/lib/mysql/
touch /var/lib/mysql/mysql.sock
if [[ ! -z "${DATABASE_UPGRADE}" ]]; then
    python /usr/share/fts/fts-database-upgrade.py
fi
/usr/bin/supervisord -c /etc/supervisord.conf
