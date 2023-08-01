#!/bin/bash

# Start factory after upgrade/reconfig is complete
# Don't delay the rest of the services
{
    /usr/sbin/gwms-factory upgrade
    # "upgrade" also performs the tasks of "reconfig"
    /usr/bin/supervisorctl start factory
} &
