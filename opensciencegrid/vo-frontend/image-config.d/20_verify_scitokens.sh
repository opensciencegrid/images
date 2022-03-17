#!/bin/bash

if [ ! -e /usr/sbin/frontend_scitoken ]; then
    echo "FATAL: /usr/sbin/frontend_scitoken is missing. This script has to be" 1>&2
    echo "       be provided by each VO. Please bind mount your own version." 1>&2
    exit 1
fi

