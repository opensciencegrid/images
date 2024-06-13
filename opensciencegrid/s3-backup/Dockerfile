FROM minio/mc:latest as mc

FROM registry.access.redhat.com/ubi9/ubi-minimal:latest

RUN microdnf install -y tar xz && \
    microdnf clean all

COPY s3-backup.sh /usr/local/bin/
COPY --from=mc /usr/bin/mc /usr/bin
COPY --from=mc /usr/bin/mc /usr/bin

ENTRYPOINT ["/usr/local/bin/s3-backup.sh"]
