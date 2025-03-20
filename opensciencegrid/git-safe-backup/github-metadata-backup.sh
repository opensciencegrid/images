#!/bin/bash
set -e

topdir=$TOP_DIR
ghmdir=$topdir/github_meta

mkdir -p $ghmdir

cd "$ghmdir"

/bin/ghb.py opensciencegrid

# git is not configured by default in the container, set sensible defaults
git config --global user.name "OSG Bot"
git config --global user.email "osg-bot@cs.wisc.edu"

cd repos/
[[ -d .git ]] || git init
git add .
if [[ $(git status --porcelain) ]]; then
  git commit -qm auto-bak
fi
