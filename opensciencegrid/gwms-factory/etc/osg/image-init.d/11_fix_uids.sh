#!/bin/bash

# this script fixes UID changes across images

if [ $(stat -c %U:%G /var/lib/condor/spool) != "condor:condor" ] ; then
  chown -R condor:condor /var/lib/condor/*
fi

for entry in /var/lib/gwms-factory/* ; do
  if [ $(stat -c %U:%G "$entry") != "gfactory:gfactory" ] ; then
    chown -R gfactory:gfactory "$entry"
  fi
done

if [ $(stat -c %U:%G /var/log/gwms-factory/server) != "gfactory:gfactory" ] ; then
  chown -R gfactory:gfactory /var/log/gwms-factory/*
fi
