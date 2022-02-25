#!/bin/bash
cd /cvmfs
if [ $? -ne 0 ]; then
  echo "/cvmfs not found!"
else
  for f in `ls`; do
    echo "Force unmount $f"
    umount -l $f
  done
fi 
