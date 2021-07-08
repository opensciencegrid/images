#!/bin/bash

set -e

S3_CREDENTIALS=/s3.creds
ENCRYPTION_KEY=/encryption.key
INPUT_DIR=/input
OUTPUT_DIR=/output
S3_ALIAS=dest

fail () {
    echo "$1"
    exit 1
}

usage () {
    fail "Usage: $0 SUBCOMMAND [ARG]

Subcommands:

  backup                 Encrypts and backs up data to S3
  ls [path]              Show contents of S3_DEST_DIR or 'path'
                         ('/' shows the contents of the S3_BUCKET root)
  restore [datetime]     Restore latest backup from S3 or backup corresponding to
                         'datetime' (format YYYYMMDD-hhmm)

Required environment variables:

- S3_BUCKET
- S3_DEST_DIR (optional for the 'ls' subcommand)
- S3_ENDPOINT

S3 credentials of the form 'access-key:secret-key' must be mounted to '$S3_CREDENTIALS'"
}


mc_backup () {
    [[ -d $INPUT_DIR ]] || fail "ERROR: Missing $INPUT_DIR dir"
    [[ -n $(ls $INPUT_DIR) ]] || fail "ERROR: no contents to backup in $INPUT_DIR"
    [[ -f $ENCRYPTION_KEY ]] || fail "ERROR: Missing encryption key, $ENCRYPTION_KEY"
    [[ -n $S3_DEST_DIR ]] || fail "ERROR: \$S3_DEST_DIR is required"

    tmpdir=$(mktemp -d)
    chmod 700 $tmpdir
    BACKUP=$tmpdir/backup-$(date +%Y%m%d-%H%M).tar
    tar -cvf $BACKUP -C $INPUT_DIR .

    # Encrypt the tarball contents using a key mounted to
    # $ENCRYPTION_KEY
    gpg --batch \
        --quiet \
        --passphrase-file $ENCRYPTION_KEY \
        --output "$BACKUP.enc" \
        --symmetric \
        --cipher-algo AES256 \
        $BACKUP

    mc cp \
       --quiet \
       $BACKUP.enc \
       "$S3_ALIAS/$S3_BUCKET/$S3_DEST_DIR/"
}


mc_ls () {
    # Treat / as the root of the bucket
    if [[ $1 == / ]]; then
        S3_DEST_DIR=""
    # otherwise, show the contents of the first arg or an existing S3_DEST_DIR
    elif [[ -n $1 ]]; then
        S3_DEST_DIR="$1"
    fi

    mc ls "$S3_ALIAS/$S3_BUCKET/$S3_DEST_DIR"
}


mc_restore () {
    [[ -d $OUTPUT_DIR ]] || fail "ERROR: Missing $OUTPUT_DIR dir"
    [[ -f $ENCRYPTION_KEY ]] || fail "ERROR: Missing decryption key, $ENCRYPTION_KEY"
    [[ -n $S3_DEST_DIR ]] || fail "ERROR: \$S3_DEST_DIR is required"

    if [[ $1 =~ [0-9]{8}+-[0-9]{4}+ ]]; then
        BACKUP="backup-$1.tar.enc"
    else
        echo "Datetime not specified, finding latest backup..."
        BACKUP=$(mc_ls | awk 'END{print $NF}')
    fi

    BACKUP_PATH=$S3_DEST_DIR/$BACKUP
    # 'mc ls' appears to return 0 if the object doesn't exist
    [[ -n $(mc_ls "$BACKUP_PATH") ]] || \
        fail "ERROR: Failed to find backup at $BACKUP_PATH"

    src_tmpfile=$(mktemp)
    mc cp \
       --quiet \
       "$S3_ALIAS/$S3_BUCKET/$BACKUP_PATH" \
       $src_tmpfile

    dcrypt_tmpfile=$(mktemp)
    gpg --batch \
        --quiet \
        --yes \
        --passphrase-file $ENCRYPTION_KEY \
        --output $dcrypt_tmpfile \
        --decrypt \
        $src_tmpfile

    tar -xvf \
        $dcrypt_tmpfile \
        -C $OUTPUT_DIR
}


# Capture the subcommand
case $# in
    0) subcommand=backup ;;
    # allow 2 args, ls/restore can take an additional arg
    [12]) subcommand=$1 ;;
    *) usage ;;
esac

# Bail if commonly required S3_* env vars aren't set
if [[ -z $S3_BUCKET ]] || [[ ! -f $S3_CREDENTIALS ]] || [[ -z $S3_ENDPOINT ]]; then
    usage
fi

# Configure alias
export MC_HOST_${S3_ALIAS}="https://$(head -1 $S3_CREDENTIALS)@${S3_ENDPOINT#https://}"

# Run subcommands
case "$subcommand" in
    backup)
        mc_backup ;;
    ls)
        shift; mc_ls "$@" ;;
    restore)
        shift; mc_restore "$@" ;;
    *)
        usage ;;
esac
