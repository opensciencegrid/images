#!/bin/bash -e

cp /tmp/fts3-configs/grid-mapfile /etc/grid-security/grid-mapfile
cp /tmp/fts3-host-pems/hostcert.pem /etc/grid-security/
chmod 644 /etc/grid-security/hostcert.pem
chown root:root /etc/grid-security/hostcert.pem
cp /tmp/fts3-host-pems/hostkey.pem /etc/grid-security/
chmod 400 /etc/grid-security/hostkey.pem
chown root:root /etc/grid-security/hostkey.pem
useradd gridftp
mkdir -p /home/gridftp/.globus/
cat /tmp/fts3-configs/etc-passwd | while read var1; do
    etcPasswd="$(echo $var1 | tr ":" " ")"
    arrayEtcPasswd=($etcPasswd)
    groupadd -f -g ${arrayEtcPasswd[3]} ${arrayEtcPasswd[0]}
    useradd ${arrayEtcPasswd[0]} -p ${arrayEtcPasswd[1]} -u ${arrayEtcPasswd[2]} -g ${arrayEtcPasswd[3]} -c "${arrayEtcPasswd[4]}" -d ${arrayEtcPasswd[6]} -s ${arrayEtcPasswd[7]}
    mkdir -p ${arrayEtcPasswd[6]}
    chown "${arrayEtcPasswd[2]}:${arrayEtcPasswd[3]}" "${arrayEtcPasswd[6]}"
done
cp /tmp/fts3-user-pems/* /home/gridftp/.globus/ 
cp /tmp/fts3-configs/fts3config /etc/fts3/fts3config
cp /tmp/fts3-configs/fts-msg-monitoring.conf /etc/fts3/fts-msg-monitoring.conf
python /usr/share/fts/fts-database-upgrade.py
fts_server
fts_bringonline
fts_msg_bulk
httpd
