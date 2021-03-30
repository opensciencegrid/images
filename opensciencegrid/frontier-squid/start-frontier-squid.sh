#!/bin/bash
# Wrapper script for starting & stopping frontier squid from supervisord

# stop squid if supervisord sends a TERM signal
trap "/etc/init.d/frontier-squid stop" TERM

# we tell squid to run in the foreground, but by telling the
#   shell to start it in the background and waiting for it we
#   prevent the shell from ignoring signals
export SQUID_START_ARGS="--foreground"
/etc/init.d/frontier-squid start &
wait
