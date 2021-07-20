#!/bin/bash

oidc-agent > /tmp/oidc-agent.env

sleep infinity

exec "$@"
