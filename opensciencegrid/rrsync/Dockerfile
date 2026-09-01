FROM almalinux:9

LABEL maintainer="OSG Software <help@osg-htc.org>"

RUN --mount=type=cache,id=dnf-9,target=/var/cache/dnf,sharing=locked \
    dnf install -y openssh-server rsync-rrsync

RUN mkdir /data

RUN mkdir -p -m0755 /run/sshd && \
    mkdir -p -m0700 /root/.ssh && \
    mkdir -p -m0700 /etc/ssh/keys

COPY --chown=root:root --chmod=0644 10-rsync.conf /etc/ssh/sshd_config.d/10-rsync.conf
COPY --chown=root:root --chmod=0644 05-hostkeys.conf /etc/ssh/sshd_config.d/05-hostkeys.conf
COPY --chown=root:root --chmod=0755 entrypoint.sh /entrypoint.sh

CMD ["/entrypoint.sh"]

EXPOSE 22/tcp
VOLUME /data
