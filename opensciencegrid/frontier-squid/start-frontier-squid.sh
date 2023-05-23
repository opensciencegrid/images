#!/bin/bash
# Wrapper script for starting & stopping frontier squid from supervisord

STARTSTOPSCRIPT=/etc/init.d/frontier-squid
if [ "$(id -u)" != 0 ]; then
    STARTSTOPSCRIPT=/usr/sbin/fn-local-squid.sh
    # crond is run under fakeroot, works better when jobs run as "root"
    # assumes running with a writable overlay
    sed -i 's/ squid / root /' /etc/cron.d/frontier-squid.cron
fi

# stop squid if supervisord sends a TERM signal
trap "$STARTSTOPSCRIPT stop" TERM

# we tell squid to run in the foreground, but by telling the
#   shell to start it in the background and waiting for it we
#   prevent the shell from ignoring signals
export SQUID_START_ARGS="--foreground"
$STARTSTOPSCRIPT start &
wait
