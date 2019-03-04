#!/bin/bash

if [[ ! -e /etc/squid/squid.conf ]]; then
  echo "Generating squid.conf..."
  /etc/squid/customize.sh < /etc/squid/squid.conf.frontierdefault > /etc/squid/squid.conf
fi

chown -R squid:squid /var/cache/squid

if [[ ! -d /var/cache/squid/00 ]]; then
  echo "Initializing cache..."
  /usr/sbin/squid -N -f /etc/squid/squid.conf -z
fi
