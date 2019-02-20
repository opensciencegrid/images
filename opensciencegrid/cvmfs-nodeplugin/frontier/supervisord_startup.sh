#!/bin/bash

# Give the chance to the pod to initialize host-specific info
source /usr/sbin/pod_init.sh

# Finish forintier-squid config initialization
/etc/init.d/frontier-squid cleancache

# Now we can actually start the supervisor
exec /usr/bin/supervisord -c /etc/supervisord.conf

