#!/bin/bash
#
# This file provides a parametrized version of
#  /etc/squid/customize.sh
# that comes from the OSG RPM.
# Note:
#   It will not be overwritten by upgrades.
# See customhelps.awk for information on predefined edit functions.
# Avoid single quotes in the awk source or you have to protect them from bash.
#

# If some of the variables are not defined, set them to their default values
# These values should reflect what is in the RPM

if [ -z "$SQUID_IPRANGE" ]; then
  echo "ERROR: SQUID_IPRANGE undefined, aborting" 1>&2
  exit 1
fi

if [ -z "$SQUID_CACHE_MEM" ]; then
  echo "ERROR: SQUID_CACHE_MEM undefined, aborting" 1>&2
  exit 1
fi

if [ -z "$SQUID_CACHE_DISK" ]; then
  echo "ERROR: SQUID_CACHE_DISK undefined, aborting" 1>&2
  exit 1
fi

# Now actually run the config command

awk --file `dirname $0`/customhelps.awk --source "{
setoption(\"acl NET_LOCAL src\", \"$SQUID_IPRANGE\")
setoption(\"cache_mem\", \"$SQUID_CACHE_MEM\")
setoptionparameter(\"cache_dir\", 3, \"$SQUID_CACHE_DISK\")
print
}"
