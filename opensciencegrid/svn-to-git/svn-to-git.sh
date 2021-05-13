#!/bin/bash

# Show errors, but allow a sleep for container debugging
err_exit() {
    echo "Error on line $(caller)" >&2
    sleep "$sleep_time"
    exit 1
}
trap 'err_exit' ERR

authors_file=/tmp/authors.txt
sleep_time="${SLEEP:-0}"

# Exit if unset variables are expanded
set -u
# And expand all our required variables
: "$AUTHORS_URL"
: "$SVN_SRC"
: "$GIT_DEST"
: "$WORK_DIR"

set -x

# Confirm SVN server is up
svn info "$SVN_SRC"

# Ensure workbench directory exists
mkdir -p "$WORK_DIR"

# Update authors file
curl "$AUTHORS_URL" -o "$authors_file"

if [ ! -f "$WORK_DIR/config" ] ; then
    # Make a new workbench
    git-svn-mirror init --from         "$SVN_SRC" \
                        --to           "$GIT_DEST" \
                        --workbench    "$WORK_DIR" \
                        --authors-file "$authors_file"

    cd "$WORK_DIR"
    git fetch || :
    git push
else
    # Update existing workbench
    git-svn-mirror update "$WORK_DIR"
fi

# Allow a sleep for container debugging
echo "Completed OK"
sleep "$sleep_time"
