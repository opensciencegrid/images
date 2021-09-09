#!/bin/bash

# Reload httpd on certificate change

# Wait for the move of the ..data symlink
inotifywait --monitor --event moved_to --timefmt %FT%T%z --format %T \
      /certs \
    | while read timestamp ; do

  echo "Config change at $timestamp. Reloading."
  supervisorctl signal USR1 httpd

done
