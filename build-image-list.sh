#!/bin/bash

# GITHUB_EVENT_BEFORE provided in env

ORG_DIR=opensciencegrid
CONTRIB=contrib
# Get the list of files changed based on the type of event
# kicking off the GHA:
# 1. For the main branch, diff the previous state of main vs
#    the current commit
# 2. For other branches (i.e., on someone's fork), diff main
#    vs the current commit
# 3. For PRs, diff the base ref vs the current commit
# 4. For everything else (e.g., dispatches), build all images
if [[ $GITHUB_EVENT_NAME == 'pull_request' ]] ||
   [[ $GITHUB_EVENT_NAME == 'push' ]]; then
     if [[ $GITHUB_EVENT_NAME == 'pull_request' ]]; then
         BASE=$(git merge-base origin/$GITHUB_BASE_REF HEAD)
     elif [[ $GITHUB_REF == 'refs/heads/main' ]]; then
         BASE=$GITHUB_EVENT_BEFORE
     else
         BASE=origin/main
     fi
     # List image root dirs where files have changed and the
     # root dir exists. Example value:
     # "opensciencegrid/vo-frontend opensciencegrid/ospool-cm"
     images=$(git diff --name-only \
                       "$BASE" \
                       "$GITHUB_SHA" |
              egrep -e "^$ORG_DIR/" -e "^$CONTRIB/" |
              cut -d/ -f -2 |
              sort |
              uniq |
              xargs -I {} find . -type d \
                                 -wholename ./{} \
                                 -printf "%P\n")
else
     # List all image root dirs. Example value:
     # "opensciencegrid/vo-frontend opensciencegrid/ospool-cm"
     images=$(find $ORG_DIR $CONTRIB \
                            -mindepth 1 \
                            -maxdepth 1 \
                            -type d \
                            -printf "%p\n")
fi

# Ensure that the generated JSON array has a member,
# otherwise GHA will throw an error about an empty matrix
# vector in subsequent steps
image_json=$(echo -n "${images:-dummy}" | jq -Rcs '.|split("\n")')
echo "::set-output name=json::$image_json"
