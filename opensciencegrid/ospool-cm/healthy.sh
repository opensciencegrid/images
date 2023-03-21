#!/bin/bash

if ! supervisorctl status >/dev/null 2>&1; then
    echo "supervisord reports failure" >&2
    exit 2
fi

# we have seen the negotiator get into a funky auth state
ERR_COUNT=$(tail -n 5000 /var/log/condor/NegotiatorLog 2>/dev/null | grep -c "ERROR: AUTHENTICATE" 2>/dev/null)
if [ $ERR_COUNT -gt 50 ]; then
    echo "Excessive auth errors in the NegotiatorLog" >&2
    exit 3
fi

exit 0

