#!/bin/bash

frontends=(
    "feglow"
    "feosgospool"
)

for frontend in ${frontends[@]}; do
    cp -Lr /home/${frontend}/ssh/ /home/${frontend}/.ssh/
    chown -R ${frontend}: /home/${frontend}/.ssh/
    chmod 0700 /home/${frontend}/.ssh/
    chmod 0644 /home/${frontend}/.ssh/id_rsa.pub
    chmod 0644 /home/${frontend}/.ssh/known_hosts
    chmod 0600 /home/${frontend}/.ssh/id_rsa
done
