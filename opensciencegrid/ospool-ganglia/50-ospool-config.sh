#!/bin/bash

set -e

# set up credentials
if [ ! -e /etc/ospool-creds/idkeys.d ]; then
    echo "Please mount /etc/ospool-creds/idkeys.d/"
    exit 1
fi
if [ ! -e /etc/ospool-creds/idtokens.d ]; then
    echo "Please mount /etc/ospool-creds/idtokens.d/"
    exit 1
fi

echo "Installing HTCondor credentials..."
cd /etc/ospool-creds/idkeys.d
for FILE in *; do
    install -o root -g root -m 0600 $FILE /etc/condor/passwords.d/$FILE
done
cd /etc/ospool-creds/idtokens.d
for FILE in *; do
    install -o root -g root -m 0600 $FILE /etc/condor/tokens.d/$FILE
done

if [ "X$DEPLOYMENT_ENV" == "Xproduction" ]; then
    cat >/etc/condor/config.d/50-ospool.config <<EOF
CONDOR_HOST = cm-1.ospool.osg-htc.org,cm-2.ospool.osg-htc.org
EOF
else
    cat >/etc/condor/config.d/50-ospool.config <<EOF
CONDOR_HOST = cm-1.ospool-itb.osg-htc.org,cm-2.ospool-itb.osg-htc.org
EOF
fi

