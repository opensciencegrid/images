#!/bin/bash

# this script prepares get_tarballs

cp /etc/gwms-factory/get_tarballs.yaml.base /etc/gwms-factory/hooks.reconfig.pre/get_tarballs.yaml
chown gfactory: /etc/gwms-factory/hooks.reconfig.pre/get_tarballs.yaml

# this line is temporary until get_tarballs is merged in the upstream gwms codebase
ln -s /opt/factools/hooks.reconfig.pre/get_tarballs.py /etc/gwms-factory/hooks.reconfig.pre/get_tarballs.py
