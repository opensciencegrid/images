#!/bin/sh

set -e

config_dir=${GWMS_FACTORY_CONFIG:-/opt/gwms-factory/}
target_dir=/etc/gwms-factory/config.d

if [ ! -e "$config_dir" ]; then
    echo "The configuration directory $config_dir does not exist; not linking"
    return
fi

mkdir -p "$target_dir"

for fname in "$config_dir"/*.xml ; do

   base_fname=$(basename "$fname")
   ln -sf "$fname" "$target_dir"/"$base_fname"

done

echo "Images linked OK from $config_dir to $target_dir"
