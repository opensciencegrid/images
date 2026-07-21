#!/bin/sh
set -e

KEY_DIR=/etc/ssh/keys

if [ ! -f "$KEY_DIR/ssh_host_rsa_key" ]; then
    for type in rsa ecdsa ed25519; do
        ssh-keygen -q -t "$type" -f "$KEY_DIR/ssh_host_${type}_key" -N ''
    done
fi

exec /usr/sbin/sshd -D -e
