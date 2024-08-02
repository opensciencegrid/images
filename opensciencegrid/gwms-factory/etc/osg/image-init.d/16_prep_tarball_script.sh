#!/bin/bash

# this script prepares get_tarballs

cp /etc/gwms-factory/get_tarballs.yaml.base /etc/gwms-factory/hooks.reconfig.pre/get_tarballs.yaml
chown gfactory: /etc/gwms-factory/hooks.reconfig.pre/get_tarballs.yaml

# enable tarball script as a pre-reconfig hook
ln -s /usr/bin/get_tarballs /etc/gwms-factory/hooks.reconfig.pre/get_tarballs
