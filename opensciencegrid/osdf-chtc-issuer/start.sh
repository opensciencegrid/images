#!/bin/sh

# Set the hostname
sed s+\{HOSTNAME\}+$HOSTNAME+g /opt/scitokens-server/etc/server-config.xml.tmpl > /opt/scitokens-server/etc/server-config.xml
sed s+\{HOSTNAME\}+$HOSTNAME+g /opt/scitokens-server/etc/proxy-config.xml.tmpl | \
sed s+\{CLIENT_ID\}+$CLIENT_ID+g | \
sed s+\{CLIENT_SECRET\}+$CLIENT_SECRET+g > /opt/scitokens-server/etc/proxy-config.xml
chgrp tomcat /opt/scitokens-server/etc/server-config.xml
chgrp tomcat /opt/scitokens-server/etc/proxy-config.xml

# As of OA4MP 5.2.9.0, QDL cannot process an ini file with a '\' -- but it can do so for QDL files.
export LDAP_PASSWORD=$(cat /opt/secrets/cilogon_ldap_password.ini | grep password | awk '{print $NF}')
sed s+@LDAP_PASSWORD@+"$(echo "$LDAP_PASSWORD" | sed 's|\\|\\\\\\|')"+ /opt/scitokens-server/var/qdl/scitokens/comanage.qdl.tmpl > /opt/scitokens-server/var/qdl/scitokens/comanage.qdl
chgrp tomcat /opt/scitokens-server/var/qdl/scitokens/comanage.qdl

# Run the boot to inject the template
${QDL_HOME}/var/scripts/boot.qdl

# Start tomcat
exec /opt/tomcat/bin/catalina.sh run

