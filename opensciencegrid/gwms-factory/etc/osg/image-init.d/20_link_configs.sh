#!/bin/sh

config_dir=${GWMS_FACTORY_CONFIG:-/opt/gwms-factory/}

if [ ! -e $config_dir ]; then
    echo "The configuration directory $config_dir does not exist; not linking"
    return
fi

for fname in $(ls $config_dir/*.xml); do

   base_fname=$(basename $fname)
   ln -sf $fname /etc/gwms-factory/config.d/$base_fname

done
