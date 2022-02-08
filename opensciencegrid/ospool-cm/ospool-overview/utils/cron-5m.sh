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

mkdir -p data

./utils/condor-stats

# straight downloads
for pair in \
    "https://stash.osgconnect.net/public/rynge/monitoring/login04/htcondor-user-stats.html data/login04-report.php" \
    "https://stash.osgconnect.net/public/rynge/monitoring/login05/htcondor-user-stats.html data/login05-report.php" \
    "https://stash.osgconnect.net/public/rynge/monitoring/login.veritas/htcondor-user-stats.html data/loginveritas-report.php" \
    "https://stash.osgconnect.net/~rynge/monitoring/osg-flock-remote-xenon/htcondor-user-stats.html data/xenon-report.php" \
    "https://stash.osgconnect.net/~rynge/monitoring/osg-flock-remote-uchicago/htcondor-user-stats.html data/uchicago-report.php" \
; do
    # put first string in $1, second in $2, ...
    set $pair
    if ! wget -O $2 "$1" >/dev/null 2>&1; then
        echo "No data" >$2
    fi
done

# stats
./utils/glidein-summary.sh >data/glidein-summary.txt

# release lock
rm -f .cron.lock

