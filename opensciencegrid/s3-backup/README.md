S3 Backup
=========

A container that archives files mounted to `/input`, encrypts the archive, and copies the encrypted archive to the
specified S3 location.
The encryption key must be mounted to `/encryption.key` and the following environment variables must be set:

- `S3_ACCESS_KEY`: S3 access key
- `S3_BUCKET`: S3 bucket to copy encrypted files to
- `S3_DEST_DIR`: directory within the S3 bucket to copy encrypted files to
- `S3_SECRET_KEY`: S3 secret key
- `S3_URL`: S3 endpoint URL. Must start with `https://`.
