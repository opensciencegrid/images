setoption("acl NET_LOCAL src", "'$SQUID_IPRANGE'")
setoption("cache_mem", "'$SQUID_CACHE_MEM'")
setoptionparameter("cache_dir", 3, "'$SQUID_CACHE_DISK'")
setoptionparameter("cache_dir", 2, "'$SQUID_CACHE_DISK_LOCATION'")
