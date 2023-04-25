#!/bin/bash

if ! (supervisorctl status frontend | grep RUNNING) >/dev/null 2>&1; then
    echo "gwms frontend is not running" >&2
    exit 1
fi

if ! supervisorctl status >/dev/null 2>&1; then
    echo "supervisord reports failure" >&2
    exit 2
fi

exit 0

