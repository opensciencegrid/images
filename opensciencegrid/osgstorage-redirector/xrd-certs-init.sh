#!/bin/bash
CERT_DIR=${CERT_DIR:-/certs}
DEST_DIR=/etc/grid-security/xrd

mkdir -p ${DEST_DIR}

# grid-security
if [ -f "$CERT_DIR/hostcert.pem" ]; then
    cp -f "$CERT_DIR/hostcert.pem" $DEST_DIR/xrdcert.pem
    cp -f "$CERT_DIR/hostkey.pem"  $DEST_DIR/xrdkey.pem
# cert-manager
elif [ -f "$CERT_DIR/tls.crt" ]; then
    cp -f "$CERT_DIR/tls.crt" $DEST_DIR/xrdcert.pem
    cp -f "$CERT_DIR/tls.key" $DEST_DIR/xrdkey.pem
else
    exit 1
fi

chmod 644 $DEST_DIR/xrdcert.pem
chmod 600 $DEST_DIR/xrdkey.pem
chown -R xrootd:xrootd $DEST_DIR
