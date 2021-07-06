FROM minio/mc:latest

COPY s3-backup.sh /usr/local/bin/

ENTRYPOINT ["/usr/local/bin/s3-backup.sh"]
