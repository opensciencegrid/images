#!/bin/bash

# this is just a temporary script until get_tarballs is merged in the upstream gwms codebase

cp /etc/gwms-factory/get_tarballs.yaml.base /etc/gwms-factory/hooks.reconfig.pre/get_tarballs.yaml
chown gfactory: /etc/gwms-factory/hooks.reconfig.pre/get_tarballs.yaml

ln -s /opt/factools/hooks.reconfig.pre/get_tarballs.py /etc/gwms-factory/hooks.reconfig.pre/get_tarballs.py
