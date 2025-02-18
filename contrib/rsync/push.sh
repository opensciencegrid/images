#!/bin/bash

set -eux

docker tag osg-htc/rsync:latest hub.opensciencegrid.org/osg-htc/rsync:latest
docker login hub.opensciencegrid.org
docker push hub.opensciencegrid.org/osg-htc/rsync:latest

