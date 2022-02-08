#!/bin/bash

# safety check
if [ ! -e main.css ]; then
    echo "ERROR: Please run this script from the top level checkout" 1>&2
    exit 1
fi

# lock
find . -maxdepth 1 -name .cron-hourly.lock -mmin +10 -exec rm -f {} \;
if [ -e .cron-hourly.lock ]; then
    exit 0
fi
touch .cron-hourly.lock

mkdir -p data

# stats
./utils/node-issues.py >data/node-issues.php.tmp
mv data/node-issues.php.tmp data/node-issues.php

# release lock
rm -f .cron-hourly.lock

