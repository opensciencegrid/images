#!/bin/bash

if [[ ! -e /etc/squid/squid.conf ]]; then
  /etc/squid/customize.sh < /etc/squid/squid.conf.frontierdefault > /etc/squid/squid.conf
fi

chown -R squid:squid /var/cache/squid

if [[ -z ${1} ]]; then
  if [[ ! -d /var/cache/squid/00 ]]; then
    echo "Initializing cache..."
    /usr/sbin/squid -N -f /etc/squid/squid.conf -z
  fi
  echo "Starting squid3..."
  exec /usr/sbin/squid -f /etc/squid/squid.conf -NYCd 1
else
  exec "$@"
fi
