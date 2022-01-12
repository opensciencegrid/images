
# If some of the variables are not defined, abort.
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

if [ -z "$SQUID_CACHE_DISK_LOCATION" ]; then
  echo "ERROR: SQUID_CACHE_DISK_LOCATION undefined, aborting" 1>&2
  exit 1
fi

