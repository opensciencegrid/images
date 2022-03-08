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
    install -o condor -g condor -m 0600 $FILE /etc/condor/tokens.d/$FILE
done

# put the right config in place
rm -f /etc/fifemon.cfg
if [ "X$DEPLOYMENT_ENV" = "Xproduction" ]; then
    ln -s /etc/fifemon.cfg-production /etc/fifemon.cfg
else
    ln -s /etc/fifemon.cfg-development /etc/fifemon.cfg
fi

