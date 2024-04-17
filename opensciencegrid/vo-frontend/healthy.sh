#!/bin/bash

if ! (supervisorctl status frontend | grep RUNNING) >/dev/null 2>&1; then
    echo "gwms frontend is not running" >&2
    exit 1
fi

if ! supervisorctl status >/dev/null 2>&1; then
    echo "supervisord reports failure" >&2
    exit 2
fi

procs_z=$(ps axo pid,stat | awk '$2 ~ /^Z/ { print $1 }' | wc -l)
if [ "$procs_z" -gt 0 ]; then
    echo "Found $procs_z zombie processes" >&2
    exit 3
fi

procs_d=$(ps axo pid,stat | awk '$2 ~ /^D/ { print $1 }' | wc -l)
if [ "$procs_d" -gt 0 ]; then
    echo "Found $procs_d deadlocked processes" >&2
    exit 4
fi

exit 0

