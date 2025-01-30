#!/bin/bash
# Wrapper script for starting & stopping frontier squid from supervisord

STARTSTOPSCRIPT=/usr/libexec/squid/frontier-squid
if [ ! -x "$STARTSTOPSCRIPT" ]; then
    # Try the < frontier-squid-5.9-3.2 path
    # FIXME: Remove when 5.9-2.1 is deprecated
    STARTSTOPSCRIPT=/etc/init.d/frontier-squid
fi

if [ "$(id -u)" != 0 ]; then
    STARTSTOPSCRIPT=/usr/sbin/fn-local-squid.sh
    if [ -f /etc/sysconfig/frontier-squid ]; then
        # When running as root this is done by /etc/init.d/frontier-squid.
        # The documentation says all variables set there should be exported.
        . /etc/sysconfig/frontier-squid
    fi
    # crond is run under fakeroot, works better when jobs run as "root".
    # Assumes running with a writable overlay.
    sed -i 's/ squid / root /' /etc/cron.d/frontier-squid.cron
fi

# stop squid if supervisord sends a TERM signal
trap "$STARTSTOPSCRIPT stop" TERM

# We tell squid to run in the foreground, but by telling the
#   shell to start it in the background and waiting for it we
#   prevent the shell from ignoring signals.
export SQUID_START_ARGS="--foreground"
$STARTSTOPSCRIPT start &
wait

# Halt the supervisord init process after squid exits
# Per https://github.com/Supervisor/supervisor/issues/712
kill -s SIGINT `cat /var/run/supervisord.pid`
