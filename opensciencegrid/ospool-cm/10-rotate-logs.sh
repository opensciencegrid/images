#!/bin/bash

# Rotate out logs that we want to keep. Our health checks uses
# logs sometimes, and we don't want them to pick up the logs
# from the previous pods, but still want to keep a set of logs
# for debugging.

TARGET_DIR=save-$(date +'%Y%m%d%H%M')

# HTCondor logs
cd /var/log/condor
mkdir -p $TARGET_DIR
find . -maxdepth 1 -type f -exec mv {} $TARGET_DIR/ \;

# only keep the last N set of saved logs
for OLD in $(ls -d -t save-*| tail -n +2); do
    rm -rf $OLD
done

