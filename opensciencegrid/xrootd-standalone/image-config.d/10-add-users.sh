#!/bin/bash
grep '".*" .*' /usr/share/osg/voms-mapfile-default  | awk '{print $2}' | xargs -n1 adduser
grep '".*" .*' /etc/grid-security/grid-mapfile  | awk '{print $2}' | xargs -n1 adduser
grep '".*" .*' /etc/grid-security/voms-mapfile | awk '{print $2}' | xargs -n1 adduser
