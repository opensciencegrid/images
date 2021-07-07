FROM minio/mc:latest

RUN microdnf install tar && \
    microdnf clean all

COPY s3-backup.sh /usr/local/bin/

ENTRYPOINT ["/usr/local/bin/s3-backup.sh"]
