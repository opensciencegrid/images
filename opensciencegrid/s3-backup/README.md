S3 Backup
=========

A container that can [encrypt and backup](#creating-backups) contents to an S3 bucket,
[view](#viewing-backups) the contents of an S3 bucket,
[restore and decrypt backups](#restoring-backups) from an S3 bucket,
and mirror data from an S3 bucket to an S3 bucket, replacing the target contents.

Requirements
------------

1.  S3 credentials of the form `access-key:secret-key` must be mounted to `/s3.creds`

1.  The following environment variables are required for all sub-commands:

    - `S3_BUCKET`: S3 target bucket
    - `S3_ENDPOINT`: S3 target endpoint, including protocol (e.g. https://play.min.io)

1.  The following environment variable is required for `backup`, `restore`, and `mirror` operations:

    - `S3_DEST_DIR`: target directory relative to `S3_BUCKET` for creating/restoring backups and `ls` operations

1.  For `mirror` operations, S3 source credentials must be mounted to `/s3.src.creds` and the following environment variables are required:

    - `S3_SRC_BUCKET`: S3 source bucket
    - `S3_SRC_ENDPOINT`: S3 source endpoint, including protocol

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
