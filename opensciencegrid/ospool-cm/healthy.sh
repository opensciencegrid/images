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

    tail -n "$lines" "$file" | count_errors.py "$starttime"
}

# we have seen the negotiator get into a funky auth state
if [ -r /var/log/condor/NegotiatorLog ]; then
    ERR_COUNT=$(count_errors /var/log/condor/NegotiatorLog 5000 "$container_start_time")
    if [ "$ERR_COUNT" -gt 50 ]; then
        echo "Excessive auth errors in the NegotiatorLog" >&2
        exit 3
    fi
fi

exit 0

