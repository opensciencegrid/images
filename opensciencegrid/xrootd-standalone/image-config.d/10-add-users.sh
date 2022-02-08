#!/bin/bash
if [ -f '/usr/share/osg/voms-mapfile-default' ]; then
    grep '".*" .*' /usr/share/osg/voms-mapfile-default  | awk '{print $NF}' | xargs -n1 adduser
fi
if [ -f '/etc/grid-security/grid-mapfile' ]; then
    grep '".*" .*' /etc/grid-security/grid-mapfile | awk '{print $NF}' | xargs -n1 adduser
fi
if [ -f '/etc/grid-security/voms-mapfile' ]; then
    grep '".*" .*' /etc/grid-security/voms-mapfile | awk '{print $NF}' | xargs -n1 adduser
fi
