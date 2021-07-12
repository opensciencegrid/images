FROM minio/mc:latest

RUN microdnf install tar xz && \
    microdnf clean all

COPY s3-backup.sh /usr/local/bin/

ENTRYPOINT ["/usr/local/bin/s3-backup.sh"]
