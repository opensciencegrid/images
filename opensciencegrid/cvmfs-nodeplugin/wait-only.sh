#!/bin/bash

#
# We use a separate bash script to get a clean exit signal (here, not in parent)
#

echo "$$" > /etc/mount-and-wait.pid

echo "Checking and Sleeping"

mps=`cat /etc/mount-and-wait.mps`
while [ 1 -lt 2 ]; do 
  # loop forever

  # make sure all the mountpoins are still alive; if not, remount
  for mp1 in $mps; do
    if [ ! -f /dev/shm/unmounting.lck ]; then
      mntd=`df -k /cvmfs/${mp1} |tail -1 |grep cvmfs2`

      if [ "x${mntd}" == "x" ]; then
        echo "WARNING: `date` Found /cvmfs/${mp1} unmounted." | tee -a /cvmfs/cvmfs-pod.log
        mount -t cvmfs ${mp1} /cvmfs/${mp1}
        rc=$?
        if [ $rc -eq 0 ]; then
          echo "INFO: `date` Mounted /cvmfs/${mp1}" | tee -a /cvmfs/cvmfs-pod.log
        else
           echo "WARNING: `date` Failed to mount /cvmfs/${mp1}" | tee -a /cvmfs/cvmfs-pod.log
        fi
      fi
    fi
  done

  sleep 30
done

