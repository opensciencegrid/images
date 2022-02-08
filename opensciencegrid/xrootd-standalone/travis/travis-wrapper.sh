#!/bin/bash -xe
# Wrapper script for building and testing XCache container images

timestamp=`date +%Y%m%d-%H%M`

./travis/build_docker.sh $timestamp
./travis/test_xrootd_standalone.sh
./travis/push_docker.sh $timestamp
