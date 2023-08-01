#!/bin/bash

# allows factory admins to add optional runtime customizations

FACTORY_INIT_PATH=/etc/gwms-factory/factory-init.d

if [ -e $FACTORY_INIT_PATH ]; then
  for x in ${FACTORY_INIT_PATH}/*.sh; do source "$x"; done
fi
