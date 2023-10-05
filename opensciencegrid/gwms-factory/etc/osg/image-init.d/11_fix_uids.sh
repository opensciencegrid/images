#!/bin/bash

# this script fixes UID changes across images

if [ $(stat -c %U:%G /var/lib/condor/spool) != "condor:condor" ] ; then
  chown -R condor:condor /var/lib/condor/*
fi

if [ $(stat -c %U:%G /var/lib/gwms-factory/web-area/stage) != "gfactory:gfactory" ] ; then
  chown -R gfactory:gfactory /var/lib/gwms-factory/*
fi

if [ $(stat -c %U:%G /var/log/gwms-factory/server) != "gfactory:gfactory" ] ; then
  chown -R gfactory:gfactory /var/log/gwms-factory/*
fi
