#!/bin/bash

# Reload httpd on certificate change

inotifywait --monitor --event modify --recursive --timefmt %FT%T%z --format %T \
      /certs \
    | while read timestamp ; do

  echo "Config change at $timestamp. Reloading."
  supervisorctl signal USR1 httpd

done
