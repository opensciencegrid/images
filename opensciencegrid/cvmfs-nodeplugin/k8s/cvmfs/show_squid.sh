#!/bin/bash

frontierIP=`kubectl get services -n cvmfs frontier-squid -o template --template={{.spec.clusterIP}}`
if [ -z "$frontierIP" ]; then
  echo "Could not find frontier service!"
  exit 1
fi
echo  "Found Squid at $frontierIP"

