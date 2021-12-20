#!/bin/sh

config_dir=${GWMS_FACTORY_CONFIG:-/opt/gwms-factory/}

for fname in $(ls $config_dir/*.xml); do

   base_fname=$(basename $fname)
   ln -sf $fname /etc/gwms-factory/config.d/$base_fname

done
