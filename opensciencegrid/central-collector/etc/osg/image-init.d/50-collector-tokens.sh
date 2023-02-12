#!/bin/bash

set -e

# set up credentials
if [ ! -e /etc/condor/idkeys.d ]; then
     echo "Please mount /etc/condor/idkeys.d/ with the signing key"
     echo "For compatibility reasons, exiting successful; this may change in the future"
     return
fi

echo "Installing HTCondor credentials..."
cd /etc/condor/idkeys.d
for FILE in *; do
    install -o root -g root -m 0600 $FILE /etc/condor/passwords.d/$FILE
done
