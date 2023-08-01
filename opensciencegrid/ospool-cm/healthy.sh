#!/bin/bash

if ! supervisorctl status >/dev/null 2>&1; then
    echo "supervisord reports failure" >&2
    exit 2
fi

container_start_time=$(stat -c %Z /proc/1)  # ctime, epoch time

count_errors () {
    local file="$1"
    local lines="$2"
    local starttime="$3"

    tail -n $lines $file | python3 -c '
import sys
import time

# container start time is in epoch format
starttime = time.gmtime(int(sys.argv[1]))

error_count = 0
for line in sys.stdin:
    # split the line into (year, time, everything else)
    split_line = line.split(" ", 2)
    try:
        # parse the timestamp -- should look like "08/01/23 11:47:36"
        linetime = time.strptime("%s %s" % split_line[0:2], "%m/%d/%y %H:%M:%S")
    except (TypeError, ValueError):
        # could not parse it; skip this line
        continue
    if linetime < starttime:
        # this happened before container startup, skip it
        continue
    if "ERROR: AUTHENTICATE" in line:
        error_count += 1

print(error_count)
' $starttime
}

# we have seen the negotiator get into a funky auth state
if [ -r /var/log/condor/NegotiatorLog ]; then
    ERR_COUNT=$(count_errors /var/log/condor/NegotiatorLog 5000 $container_start_time)
    if [ $ERR_COUNT -gt 50 ]; then
        echo "Excessive auth errors in the NegotiatorLog" >&2
        exit 3
    fi
fi

exit 0

