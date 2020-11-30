#!/bin/bash

# temporary until https://its.cern.ch/jira/browse/FTAPPDEVEL-172
sed -i 's/$SQUID$/$SQUID $SQUID_START_ARGS/' /usr/sbin/fn-local-squid.sh
