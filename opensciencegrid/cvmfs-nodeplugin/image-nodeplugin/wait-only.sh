#!/bin/bash

#
# We use a separate bash script to get a clean exit signal (here, not in parent)
#

echo "$$" > /etc/mount-and-wait.pid

echo "Sleeping"
sleep infinity

