#!/bin/bash

cd $(dirname $0)

openssl req -x509 -newkey rsa:4096 -keyout tls.key -out tls.crt -days 365 -subj '/CN=localhost' -nodes
