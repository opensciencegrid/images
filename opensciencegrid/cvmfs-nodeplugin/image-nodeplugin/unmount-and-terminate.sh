#!/bin/bash

# do not die on signal, try to complete
trap "echo Unmount-Signal-Received  | tee -a /cvmfs/cvmfs-pod.log" SIGTERM SIGINT

maxtries=20
tries=0

# prevent startup race condition
while [ ! -f /etc/mount-and-wait.pid ]; do
     echo "Missing mount-and-wait.pid"  | tee -a /cvmfs/cvmfs-pod.log
     sleep 1
     let tries=1+$tries
     if [ $tries -ge $maxtries ]; then
       break
     fi
done


mps=`cat /etc/mount-and-wait.mps`

# cleanup
for mp1 in $mps; do
   umount /cvmfs/${mp1}
   rc=$?
   while [ $rc -ne 0 ]; do
     sleep 1
     echo "Retrying unmounting ${mp1}"  | tee -a /cvmfs/cvmfs-pod.log
     umount /cvmfs/${mp1}
     rc=$?
     let tries=1+$tries
     if [ $tries -ge $maxtries ]; then 
       break
     fi
   done
   rmdir /cvmfs/${mp1}
   echo "Unmounted ${mp1}"  | tee -a /cvmfs/cvmfs-pod.log
done


pidk=`cat /etc/mount-and-wait.pid`
if [ "x${pidk}" != "x" ]; then
  # hard kill the waiting process, should not be doing anything but sleep
  kill -9 "$pidk"
  echo "Killed $pidk"   | tee -a /cvmfs/cvmfs-pod.log
else
  echo "WARNING: /etc/mount-and-wait.pid not found"  | tee -a /cvmfs/cvmfs-pod.log
fi
