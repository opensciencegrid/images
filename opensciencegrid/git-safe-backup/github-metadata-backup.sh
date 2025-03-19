#!/bin/bash
set -e

topdir=$TOP_DIR
ghmdir=$topdir/github_meta
local_ghmdir=/tmp/github_meta

mkdir -p $ghmdir
mkdir -p $local_ghmdir

# due to the enormous number of files involved:
#   - origin bare repo should be placed on a volume-mounted storage device
#   - working copy can be kept in container ephemeral storage


cd "$local_ghmdir"

/bin/ghb.py opensciencegrid

cd repos/
[[ -d .git ]] || git init
git add .
if [[ $(git status --porcelain) ]]; then
  git commit -qm auto-bak
  git push
fi
