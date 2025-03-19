#!/bin/bash
set -e

topdir=$TOP_DIR
ghmdir=$topdir/github_meta
local_ghmdir=/tmp/github_meta

mkdir -p $ghmdir
mkdir -p $local_ghmdir

# due to the enormous number of files involved:
#   - origin bare repo on AFS is $ghmdir/repos.git
#   - working copy is on local disk under $local_ghmdir

# Note:
#   - pyjwt and PyGithub libs installed locally on moria under ~/.local/lib
#   - See ~/git/ for the versions installed, with: ./setup.py build;
#                                                  ./setup.py install --user

cd "$local_ghmdir"

/bin/ghb.py opensciencegrid

cd repos/
[[ -d .git ]] || git init
git add .
if [[ $(git status --porcelain) ]]; then
  git commit -qm auto-bak
  git push
fi
