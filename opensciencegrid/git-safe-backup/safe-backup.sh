#!/bin/bash

topdir=$TOP_DIR
bakdir=$topdir/repo
lockfile=/tmp/$(id -un)/.gitbackups.lk
tsdir=/var/tmp/git-safe-backup

# create directories if they don't exist
mkdir -p $bakdir

# list file of git clone urls, path can be absolute or relative to bakdir
git_remotes_listfile=$REMOTES_LIST

email_from=$EMAIL_FROM
email_to=$EMAIL_TO

datelog () {
  echo "$(date): $*"
}

# initialize (if missing) and fetch current remote git url
safebakrepo () {
  ( # run in subshell that exits on errors
    set -e
    remote=${remote%/}
    if [[ $remote =~ ([^/]+/[^/]+)$ ]]; then
      repo=${BASH_REMATCH[1]}
    else
      repo=${remote##*/}
    fi
    [[ $repo = *.git ]] || repo+=.git
    if [[ -e $repo/NO_FETCH ]]; then
        datelog "Skipping $remote (NO_FETCH file present)"
        return
    fi

    [[ -d $repo ]] || initrepo

    datelog "Fetching $remote"
    cd "$repo"
    timeout --kill-after=20s 240s git fetch
    safetags
    touch last-success-mtime
  )
}

# initialize new bare repo to mirror current remote git url
initrepo () {
  (
    datelog "Initializing backup repo for $remote"
    mkdir -p "$repo"
    cd "$repo"
    git init --bare
    git remote add origin "$remote"
    git config transfer.fsckObjects  true
    git config core.logAllRefUpdates true

    # allow non-ff pull request updates and select wip branches, and
    # ff-only updates for all other refs
    wip_branches=("itb*" "preview-*" "wip/*")
    git config remote.origin.fetch '+refs/pull/*:refs/pull/*'
    for b in "${wip_branches[@]}"; do
      git config --add remote.origin.fetch "+refs/heads/$b:refs/heads/$b"
    done
    git config --add remote.origin.fetch 'refs/*:refs/*'
  )
}

# create reflog for all tags; detect tag updates
safetags () {
    local ret=0
    for tag in $(git tag); do
        taglog=logs/refs/tags/$tag
        tagdir=${taglog%/*}
        [[ -d $tagdir ]] || mkdir -p $tagdir
        [[ -e $taglog ]] || touch $taglog
        if [[ -s $taglog ]]; then
            echo "Warning: tag '$tag' has a history..."
            git reflog refs/tags/$tag
            echo
            touch $tmpd/failures-detected
            ret=1
        fi
    done
    return $ret
}

email_errors () {
    /bin/send_mail.py "Git[Hub] Safe-Backup errors" "$email_from" $email_to <(
    { echo "Errors detected for backup run at $(date)."
      echo
      echo "See /p/condor/workspaces/vdt/git/doc/error-recovery-notes.txt for instructions."
      echo ---
      echo
      cat $tmpd/backups.log
    })
}

cd "$bakdir"
tmpd=$(mktemp -d)
trap 'rm -rf "$tmpd"' EXIT

{ # log all stdout/stderr from this section

[[ -e $tsdir ]] || mkdir -m755 $tsdir
mkdir -p "$(dirname "$lockfile")"
# attempt to acquire lock before doing fetches
exec 99>> "$lockfile"

if ! flock -n 99; then
    datelog 'Could not acquire lock (previous run still active) -' \
            'Please investigate!!!'
    touch $tmpd/failures-detected
else
    remotes=( $(grep '^[^#]' "$git_remotes_listfile") )

    for remote in "${remotes[@]}"; do
        for (( retries=3; retries > 0; retries-- )); do
            safebakrepo_out=$(safebakrepo 2>&1)
            safebakrepo_ret=$?
            echo "$safebakrepo_out"
            grep -q "Operation now in progress" <<< "$safebakrepo_out" || break
            sleep 30
        done
        [[ $safebakrepo_ret -eq 0 ]] || touch $tmpd/failures-detected
    done
fi
echo ---
} 2>&1 | tee $tmpd/backups.log

if [[ -e $tmpd/failures-detected ]]; then
    if [[ -t 1 ]]; then
        echo errors detected...
    fi
    # send error email if our last failure email was sent more than
    # a day ago, or if there was a successful run since then
    touch -d "$(date -d '1 day ago')" $tmpd/yesterday-mtime
    if [[ $tsdir/last-failure-email-mtime -ot $tmpd/yesterday-mtime     ||
          $tsdir/last-failure-email-mtime -ot $tsdir/last-success-mtime ]]; then
        email_errors 99>&-  # don't pass lock fd to mailer
        touch $tsdir/last-failure-email-mtime
    fi
    cp $tmpd/backups.log $tsdir/last-failure-msg
else
    touch $tsdir/last-success-mtime
fi

# copy logrotate config to local disk because logrotate tries to lock it
# cp $srcdir/backups.logrotate $tmpd/backups.logrotate
# /usr/sbin/logrotate --state $tmpd/logrotate.state $tmpd/backups.logrotate
