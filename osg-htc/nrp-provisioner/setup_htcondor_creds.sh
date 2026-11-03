#!/bin/bash
su provisioner -c "mkdir -p /home/provisioner/.condor/tokens.d && chmod -R go-rwx /home/provisioner/.condor"
cp /etc/condor/tokens.d/* /home/provisioner/.condor/tokens.d/ && chown -R provisioner /home/provisioner/.condor

if [ "x${HTCONDOR_QUERY_INSECURE}" == "xyes" ]; then
  su provisioner -c "echo export _CONDOR_SEC_CLIENT_AUTHENTICATION=OPTIONAL >> /home/provisioner/.bashrc"
  su provisioner -c "echo export _CONDOR_SEC_CLIENT_INTEGRITY=OPTIONAL >> /home/provisioner/.bashrc"
  su provisioner -c "echo export _CONDOR_SEC_CLIENT_ENCRYPTION=OPTIONAL >> /home/provisioner/.bashrc"
fi

