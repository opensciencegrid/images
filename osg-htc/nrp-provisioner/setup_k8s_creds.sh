#!/bin/bash
su provisioner -c "touch /home/provisioner/.bashrc"

su provisioner -c "echo export KUBERNETES_SERVICE_PORT=${KUBERNETES_SERVICE_PORT} >> /home/provisioner/.bashrc"
su provisioner -c "echo export KUBERNETES_SERVICE_HOST=${KUBERNETES_SERVICE_HOST} >> /home/provisioner/.bashrc"

#also add the other kubernetes-related env variables
su provisioner -c "echo export K8S_NAMESPACE=${K8S_NAMESPACE} >> /home/provisioner/.bashrc"
