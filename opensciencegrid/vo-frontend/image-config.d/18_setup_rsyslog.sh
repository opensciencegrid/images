#!/bin/bash -x

if [[ -e /opt/rsyslog-pilot ]]; then
    pushd /opt/rsyslog-pilot/
    ./create_rsyslog_tarball.sh rsyslog.tar.gz
    popd
fi

