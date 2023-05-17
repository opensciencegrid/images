#!/bin/bash

autoconf_dir=/etc/osg-gfactory/OSG_autoconf
missing_url=http://gfactory-2.opensciencegrid.org/missing.yml

if [ ! -d $autoconf_dir ];then
    echo "$autoconf_dir does not exist; skipping"
    exit 0
fi

echo "{}" > ${autoconf_dir}/OSG.yml
chown gfactory: ${autoconf_dir}/OSG.yml

curl -sSf -o ${autoconf_dir}/missing.yml ${missing_url}
if [ $? -ne 0 ];then
    echo "failed to download ${missing_url}; skipping"
    exit 0
fi
chown gfactory: ${autoconf_dir}/missing.yml
