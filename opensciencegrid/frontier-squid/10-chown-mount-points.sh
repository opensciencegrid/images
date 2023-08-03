#!/bin/bash

# Attempt to recursively set the ownership of /var/log/squid and /var/cache/squid to
# squid:root. Exit on failure, since incorrect ownership prevents squid from running.

SQUID_DIRS=(/var/log/squid /var/cache/squid)
OWNER=squid
GROUP=root
EXIT_CODE=13

change_dir_permissions() {
  squid_dir=$1
  # Only chown if the top level directory has incorrect permissions
  if [ $(stat -c %U:%G $squid_dir) == "$OWNER:$GROUP" ] ; then
    return
  fi

  # Recursively chown the given directory, exiting on failure
  if ! chown -R "$OWNER:$GROUP" "$squid_dir" ; then 
    echo "Error: Unable to set ownership of mounted $squid_dir to $OWNER:$GROUP. frontier-squid is unable to run."
    exit $EXIT_CODE
  fi
}

# Only attempt to chown if the script is being run as root
if [[ $(id -u) -eq 0 ]] ; then
  for dir in ${SQUID_DIRS[@]}; do
    change_dir_permissions $dir
  done
fi
