#!/bin/bash

if [ "x${SQUID_URI}" == "x" ]; then
  echo "Missing SQUID_URI" 1>&2
  exit 1
fi
echo "CVMFS_HTTP_PROXY=\"${SQUID_URI}\"" >/etc/cvmfs/default.local


if [ "x${QUOTA_LIMIT}" != "x" ]; then
  echo "CVMFS_QUOTA_LIMIT=${QUOTA_LIMIT}" >> /etc/cvmfs/default.local
fi


if [ "x${MOUNT_REPOS}" == "x" ]; then
  echo "Missing MOUNT_REPOS" 1>&2
  exit 1
fi

# do not die on signal, try to cleanup as fast as you can
trap "/usr/local/sbin/force_unmount.sh" SIGTERM SIGINT

mps=""
for mp in `echo ${MOUNT_REPOS} |tr , ' '` ; do 
 echo "INFO: `date` Processing /cvmfs/${mp}." | tee -a /cvmfs/cvmfs-pod.log

 mkdir -p /cvmfs/${mp}
 rc=$?
 if [ ${rc} -ne 0 ]; then
   echo "INFO: Removing existing /cvmfs/${mp}." | tee -a /cvmfs/cvmfs-pod.log
   rmdir /cvmfs/${mp}
   # no error checking ... if it failed, we will catch below
   mkdir -p /cvmfs/${mp}
   rc=$?
 fi

 if [ ${rc} -ne 0 ]; then
   # force clean if already there
   echo "WARNING: Found /cvmfs/${mp}. Unmounting." | tee -a /cvmfs/cvmfs-pod.log
   umount /cvmfs/${mp}
   rc=$?
   if [ $rc -ne 0 ]; then
     echo "WARNING: Using lazy umount for /cvmfs/${mp}" | tee -a /cvmfs/cvmfs-pod.log
     umount -l /cvmfs/${mp}
     sleep 5 # give time for the system to catch up
   fi
   rmdir /cvmfs/${mp}

   mkdir -p /cvmfs/${mp}
   rc=$?
 fi

 # try without checking rc... will fail if mkdir failed
 echo "INFO: Mounting /cvmfs/${mp}." | tee -a /cvmfs/cvmfs-pod.log
 mount -t cvmfs ${mp} /cvmfs/${mp}
 rc=$?
 if [ ${rc} -ne 0 ] ; then
   echo "WARNING: Failed to mount $mp, retrying"  | tee -a /cvmfs/cvmfs-pod.log
   sleep 15
   mkdir -p /cvmfs/${mp}
   mount -t cvmfs ${mp} /cvmfs/${mp}
   rc=$?
 fi

 if [ ${rc} -eq 0 ] ; then
   echo "INFO: Mounted /cvmfs/${mp}" | tee -a /cvmfs/cvmfs-pod.log
   mps="$mp $mps" #save them in reverse order
 else
   echo "ERROR: Failed to mount $mp"  | tee -a /cvmfs/cvmfs-pod.log

   # cleanup
   for mp1 in $mps; do
     umount /cvmfs/${mp1}
   done
   exit 2
 fi
done

echo "$mps" > /etc/mount-and-wait.mps

echo "INFO: `date` CVMFS mountpoints started: $mps"  | tee -a /cvmfs/cvmfs-pod.log
/usr/local/sbin/wait-only.sh
echo "INFO: `date` Terminating"   | tee -a /cvmfs/cvmfs-pod.log

# cleanup

# first try the proper way
for mp1 in $mps; do
   if [ -d /cvmfs/${mp1} ]; then
     umount /cvmfs/${mp1}
     rc=$?
     if [ $rc -ne 0 ]; then
       echo "WARNING: Failed unmounting ${mp1}"  | tee -a /cvmfs/cvmfs-pod.log
     else
       rmdir /cvmfs/${mp1}
       echo "INFO: Unmounted ${mp1}"  | tee -a /cvmfs/cvmfs-pod.log
     fi
   fi
done

# now do a pass with the most fail-safe option possible
for mp1 in $mps; do
  echo "INFO: Attempting lazy umount of ${mp1}"  | tee -a /cvmfs/cvmfs-pod.log
  umount -l /cvmfs/${mp1}
  if [ $? -eq 0 ]; then 
   echo "INFO: Lazy unmounted ${mp1}"  | tee -a /cvmfs/cvmfs-pod.log
  fi
done

# wait a tiny bit to make sure everything is cleaned up properly
sleep 2

echo "INFO: `date` Bye"  | tee -a /cvmfs/cvmfs-pod.log

