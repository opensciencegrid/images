#!/bin/bash

oidc-agent | grep -vw "echo" > /tmp/oidc-agent.env

sleep infinity
