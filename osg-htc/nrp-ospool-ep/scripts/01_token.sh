#!/bin/bash

#
# osgvo-pilot expects the token as an env variable
#

token_file=/etc/condor/tokens.d/prp-wn.token
if [ ! -r "$token_file" ]; then
    echo "ERROR: required token file '$token_file' is missing or unreadable" >&2
    exit 1
fi

read TOKEN < "$token_file"
export TOKEN
