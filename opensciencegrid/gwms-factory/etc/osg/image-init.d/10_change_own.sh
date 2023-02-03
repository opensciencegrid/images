#!/bin/bash

cp /etc/gwms-factory/glideinWMS.xml.base /etc/gwms-factory/glideinWMS.xml
chown gfactory: /etc/gwms-factory/glideinWMS.xml

chown gfactory: /etc/gwms-factory/config.d

mkdir -p /var/lib/condor/{schedd_glideins2,schedd_glideins3,schedd_glideins4,schedd_glideins5}/spool
chown condor: /var/lib/condor/{schedd_glideins2,schedd_glideins3,schedd_glideins4,schedd_glideins5}/spool

mkdir -p /var/lib/gwms-factory/{client-proxies,creation,server-credentials,web-area,web-base,work-dir}
chown gfactory: /var/lib/gwms-factory/{client-proxies,creation,server-credentials,web-area,web-base,work-dir}
