#!/bin/bash

cp /etc/gwms-factory/get_tarballs.yaml.base /etc/gwms-factory/hooks.reconfig.pre/get_tarballs.yaml

ln -s /opt/factools/hooks.reconfig.pre/get_tarballs.py /etc/gwms-factory/hooks.reconfig.pre/get_tarballs.py
