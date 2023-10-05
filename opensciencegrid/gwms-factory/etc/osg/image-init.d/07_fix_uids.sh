#!/bin/bash

# this script fixes UID changes across images

for entry in /var/lib/condor/* ; do
  if [ $(stat -c %U:%G "$entry") != "condor:condor" ] ; then
    chown -R condor:condor "$entry"
  fi
done

for entry in /var/lib/gwms-factory/* /var/log/gwms-factory/* ; do
  if [ $(stat -c %U:%G "$entry") != "gfactory:gfactory" ] ; then
    chown -R gfactory:gfactory "$entry"
  fi
done
