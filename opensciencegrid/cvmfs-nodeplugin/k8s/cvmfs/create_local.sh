#!/bin/bash

frontierIP=`kubectl get services -n cvmfs frontier-squid -o template --template={{.spec.clusterIP}}`
if [ -z "$frontierIP" ]; then
  echo "Could not find frontier service!"
  exit 1
fi
echo "# WARNING: This file will be re-created at next make" >default.local
cat default.local.template | sed "s/FRONTIERSQUIDSERVICE/$frontierIP/g" >> default.local

