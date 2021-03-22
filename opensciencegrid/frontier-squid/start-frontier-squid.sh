#!/bin/bash
# Wrapper script for starting & stopping frontier squid from supervisord

# stop squid if supervisord sends a TERM signal
trap "/usr/sbin/fn-local-squid.sh stop" TERM

# we tell squid to run in the foreground, but by telling the
#   shell to start it in the background and waiting for it we
#   prevent the shell from ignoring signals
export SQUID_START_ARGS="--foreground"
/usr/sbin/fn-local-squid.sh start &
wait
