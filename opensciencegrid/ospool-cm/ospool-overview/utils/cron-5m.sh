#!/bin/bash

# safety check
if [ ! -e main.css ]; then
    echo "ERROR: Please run this script from the top level checkout" 1>&2
    exit 1
fi

# lock
find . -maxdepth 1 -name .cron.lock -mmin +10 -exec rm -f {} \;
if [ -e .cron.lock ]; then
    exit 0
fi
touch .cron.lock

export _CONDOR_COLLECTOR_HOST=cm-1.ospool.osg-htc.org

mkdir -p data

./utils/condor-stats

# stats
./utils/glidein-summary.sh >data/glidein-summary.txt

# release lock
rm -f .cron.lock

