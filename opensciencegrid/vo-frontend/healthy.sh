#!/bin/bash

failures=$(supervisorctl status | grep -Ev 'container_cleanup|RUNNING')
if [ -n "$failures" ]; then
    echo "supervisord non-RUNNING service:" >&2
    echo "$failures" >&2
    exit 2
fi

exit 0

