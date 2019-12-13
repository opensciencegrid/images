#!/bin/bash -xe
# Script for building and pushing Frontier Squid docker images

org='opensciencegrid'
timestamp=`date +%Y%m%d-%H%M`
docker_repos='xrootd-standalone'

for repo in $docker_repos; do
    docker build \
           -t $org/$repo:fresh \
           -t $org/$repo:$timestamp \
           .
done

