#!/bin/bash

# Attempt to recursively set the ownership of /var/log/squid and /var/cache/squid to
# squid:root. Exit on failure, since incorrect ownership prevents squid from running.

SQUID_DIRS=(/var/log/squid /var/cache/squid)
OWNER=squid
GROUP=root
EXIT_CODE=13

for squid_dir in ${SQUID_DIRS[@]}; do
  if ! find $squid_dir | xargs chown $OWNER:$GROUP ; then 
    echo "Error: Unable to set ownership of mounted $squid_dir to $OWNER:$GROUP. frontier-squid is unable to run."
    exit $EXIT_CODE
  fi
done
