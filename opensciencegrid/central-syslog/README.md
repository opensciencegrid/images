
OSG Central Syslog Server Docker image
======================================

This repository contains a simple Docker image for the OSG central syslog
server.

It is designed to listen on TCP port 6514 and have:

- TLS host certificate and key mounted as `tls.crt` and `tls.key` in
  `/etc/pki/rsyslog-server`.
- The corresponding CA (public) certificate mounted as `tls.crt` in
  `/etc/pki/rsyslog-ca`.

Example invocation:

```
podman run -p 6514:6514 \
   -v $PWD/secrets/server:/etc/pki/rsyslog-server \
   -v $PWD/secrets/ca:/etc/pki/rsyslog-ca \
   -ti hub.opensciencegrid.org/opensciencegrid/central-syslog:3.6-el8-release
```
