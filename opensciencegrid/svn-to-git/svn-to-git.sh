#!/bin/bash

# Show errors, but allow a sleep for container debugging
err_exit() {
    echo "Error on line $(caller)" >&2
    sleep "$sleep_err"
    exit 1
}
trap 'err_exit' ERR

authors_file=/tmp/authors.txt
sleep_err="${SLEEP_ERR:-0}"

# Exit if unset variables are expanded
set -u
# And expand all our required variables
: "$AUTHORS_URL"
: "$SVN_BASE"
: "$SVN_PATH"
: "$GIT_DEST"
: "$WORK_DIR"

set -x

# Confirm SVN server is up
svn info "$SVN_BASE"

# Ensure workbench directory exists
mkdir -p "$WORK_DIR"

# Update authors file
curl "$AUTHORS_URL" -o "$authors_file"

if [ ! -f "$WORK_DIR/config" ] ; then
    # Make a new working directory
    git clone --bare "$GIT_DEST" "$WORK_DIR"

    pushd "$WORK_DIR"
    git config svn.authorsfile         "$authors_file"
    git config svn-remote.svn.url      "$SVN_BASE"
    git config svn-remote.svn.fetch    "$SVN_PATH/trunk:refs/heads/trunk"
    git config svn-remote.svn.branches "$SVN_PATH/branches/*:refs/heads/*"
    git config svn-remote.svn.tags     "$SVN_PATH/tags/*:refs/tags/*"
    popd
fi

pushd "$WORK_DIR"
git svn fetch
git push --all
git push --tags

echo "Completed OK"
