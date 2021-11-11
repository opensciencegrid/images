#!/bin/bash

CERT_DIR=${CERT_DIR:-/certs}

# Update certificate on change

# Wait for the move of the ..data symlink
inotifywait --monitor --event moved_to --timefmt %FT%T%z --format %T \
      $CERT_DIR \
    | while read timestamp ; do

  echo "Certificate change at $timestamp."
  /usr/local/sbin/xrd-certs-init.sh
  # XRootD doesn't automatically reload certs on change
  supervisorctl restart xrootd-redirector

done
