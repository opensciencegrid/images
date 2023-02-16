#!/bin/sh

if [[ -d /etc/condor/config.d-boot ]]; then
    echo "Copying initial configs from /etc/condor/config.d-boot/ to /etc/condor/config.d/"
    cp /etc/condor/config.d-boot/* /etc/condor/config.d/
fi

if [[ -d /etc/condor/passwords.d-boot ]]; then
    echo "Copying initial keys from /etc/condor/passwords.d-boot/ to /etc/condor/passwords.d/"
    cp /etc/condor/passwords.d-boot/* /etc/condor/passwords.d/
fi

