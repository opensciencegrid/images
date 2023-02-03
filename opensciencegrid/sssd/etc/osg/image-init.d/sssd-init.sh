#!/bin/sh
# Ensure that sssd's "pipes" directory has the required structure.

set -eu

_pipes_dir=/var/lib/sss/pipes/
_private_pipes_dir=/var/lib/sss/pipes/private/

mkdir -p           "${_pipes_dir}"
chown sssd:sssd    "${_pipes_dir}"
chmod u=rwx,go=rx  "${_pipes_dir}"

mkdir -p           "${_private_pipes_dir}"
chown root:root    "${_private_pipes_dir}"
chmod u=rwx,go=    "${_private_pipes_dir}"
