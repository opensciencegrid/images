#!/bin/bash

if ! supervisorctl status >/dev/null 2>&1; then
    echo "supervisord reports failure" >&2
    exit 2
fi

container_start_time=$(stat -c %Z /proc/1)  # ctime, epoch time

# we have seen the negotiator get into a funky auth state
if [ -r /var/log/condor/NegotiatorLog ]; then
    ERR_COUNT=$(tail -n 5000 /var/log/condor/NegotiatorLog | count_errors_since.py "$container_start_time")
    if [ "$ERR_COUNT" -gt 50 ]; then
        echo "Excessive auth errors in the NegotiatorLog" >&2
        exit 3
    fi
fi

procs_z=$(ps axo pid,stat | awk '$2 ~ /^Z/ { print $1 }' | wc -l)
if [ "$procs_z" -gt 3 ]; then
    echo "Found $procs_z zombie (Z) processes" >&2
    exit 4
fi

procs_d=$(ps axo pid,stat | awk '$2 ~ /^D/ { print $1 }' | wc -l)
if [ "$procs_d" -gt 15 ]; then
    echo "Found $procs_d uninterruptible (D) processes" >&2
    exit 5
fi

exit 0

