S3 Backup
=========

A container that can [encrypt and backup](#creating-backups) contents to an S3 bucket,
[view](#viewing-backups) the contents of an S3 bucket,
and [restore and decrypt backups](#restoring-backups) from an S3 bucket.

The following environment variables are required for all sub-commands:

- `S3_ACCESS_KEY`: S3 access key
- `S3_BUCKET`: S3 bucket
- `S3_SECRET_KEY`: S3 secret key
- `S3_URL`: S3 endpoint URL. Must start with `https://`.

Required for `backup` and `restore` operations:

- `S3_DEST_DIR`: target directory relative to `S3_BUCKET` for creating/restoring backups and `ls` operations


Creating Backups
----------------

In addition to the above environment variable requirements,
creating backups requires data mounted to `/input` and an encryption key mounted to `/encryption.key`.
Backup is the default operation.

```
docker run -it \
           -v /path/to/encryption/key:/encryption.key \
           -v /dir/containing/data/for/backup:/input \
           --env-file path/to/environment/file \
           s3-backup:release
```

Viewing Backups
---------------

Show all objects in `S3_BUCKET/S3_DESTDIR`:

```
docker run -it \
           --env-file path/to/environment/file \
           s3-backup:release \
           ls
```

Show all objects in `S3_BUCKET/<ALTERNATE_DIR>`:

```
docker run -it \
           --env-file path/to/environment/file \
           s3-backup:release \
           ls <ALTERNATE DIR>
```

To see the contents of the bucket root:

```
docker run -it \
           --env-file path/to/environment/file \
           s3-backup:release \
           ls /
```

Restoring Backups
-----------------

In addition to the above environment variable requirements,
creating backups requires an output directory mounted to `/output` and a decryption key mounted to `/encryption.key`.

Copy and decrypt the latest backup:

```
docker run -it \
           -v /path/to/encryption/key:/encryption.key \
           -v /target/restore/dir:/output \
           --env-file path/to/environment/file \
           s3-backup:release
           restore
```

Copy and decrypt the backup corresponding to a specific datetime, replacing `<YYYYMMDD-mmdd>` with the datetime:

```
docker run -it \
           -v /path/to/encryption/key:/encryption.key \
           -v /target/restore/dir:/output \
           --env-file path/to/environment/file \
           s3-backup:release
           restore <YYYYMMDD-mmdd>
```
