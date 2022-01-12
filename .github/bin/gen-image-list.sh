#!/bin/bash

# dir containing subdirs with Dockerfiles
IMAGE_DIR=$1

ls -m "$IMAGE_DIR" | tr -d '\n' | jq -Rcs '.|split(", ")'
# if [[ $GITHUB_EVENT_NAME != "push" ]]; then
    
# else
#     echo $(ls -m "$PATH" | tr -d '\n' | jq -Rcs '.|split(", ")')
# fi


