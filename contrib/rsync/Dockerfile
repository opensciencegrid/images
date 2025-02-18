FROM almalinux:9

LABEL maintainer OSG Software <help@osg-htc.org>

RUN --mount=type=cache,id=dnf-9,target=/var/cache/dnf,sharing=locked \
    dnf install -y rsync

RUN mkdir /data

COPY --chown=root:root --chmod=0644 rsyncd-example.conf /etc/rsyncd.conf

CMD ["/usr/bin/rsync", "--daemon", "--no-detach", "--port=873", "--verbose", "--log-file=/dev/stdout"]

EXPOSE 873/tcp
VOLUME /data

