#!/bin/bash

set -e

ENCRYPTION_KEY=/encryption.key

usage () {
    cat <<EOF
This tool requires an encryption key in /encryption-key
and the following environment variables
- S3_ACCESS_KEY
- S3_BUCKET
- S3_DEST_DIR
- S3_SECRET_KEY
- S3_URL (must start with https://)
EOF
    exit 1
}

# S3_* env vars are required, the url must be properly formatted, and
# there must be an encryption key
if [[ -z $S3_ACCESS_KEY$S3_BUCKET$S3_DEST_DIR$S3_SECRET_KEY$S3_URL ]] ||
       [[ $S3_URL != https://* ]] ||
       [[ ! -f $ENCRYPTION_KEY ]]; then
    usage
fi

# Create an alias for the S3 endpoint/credentials
# S3_URL must start with "https://"
mc alias set dest "$S3_URL" "$S3_ACCESS_KEY" "$S3_SECRET_KEY"


tmpdir=$(mktemp -d)
chmod 700 $tmpdir
backup=$tmpdir/backup-$(date +%Y%m%d-%H%M).tar
tar -cvf $backup /input/*

# Encrypt the tarball contents using a key mounted to
# $ENCRYPTION_KEY
gpg --batch \
    --passphrase-file $ENCRYPTION_KEY \
    --output "$backup.enc" \
    --symmetric \
    --cipher-algo AES256 \
    $backup

# Copy 
mc cp \
   --preserve \
   $backup \
   "dest/$S3_BUCKET/$S3_DEST_DIR/"
