#!/bin/bash

# this is just a temporary script until we get some fixes in upstream gwms to make autconf work first time

#autoconf_dir=/etc/osg-gfactory/OSG_autoconf
#missing_url=http://gfactory-2.opensciencegrid.org/missing.yml

#if [ ! -d $autoconf_dir ];then
#    echo "$autoconf_dir does not exist; skipping"
#    return
#fi

#echo "{}" > ${autoconf_dir}/OSG.yml
#chown gfactory: ${autoconf_dir}/OSG.yml

cp /etc/gwms-factory/OSG_autoconf.yaml.base /etc/gwms-factory/OSG_autoconf.yaml
#chown gfactory: /etc/gwms-factory/OSG_autoconf.yaml

#curl -sSf -o ${autoconf_dir}/missing.yml ${missing_url}
#if [ $? -ne 0 ];then
#    echo "failed to download ${missing_url}; skipping"
#    return
#fi
#chown gfactory: ${autoconf_dir}/missing.yml
