FROM almalinux:9

LABEL maintainer "OSG Software <help@osg-htc.org>"

RUN --mount=type=cache,id=dnf-el9,target=/var/cache/dnf,sharing=locked \
    dnf -y install crontabs cronie epel-release /usr/sbin/runuser procps-ng && \
    crb enable && \
    dnf -y install apptainer python3-pyyaml && \
    useradd \
        --system \
        --home-dir /ospool/images \
        -u 950 \
        images && \
    install -o images -g images -d /ospool/images && \
    install -o images -g images -d /ospool/images-scripts

COPY --chmod=0644 images.yaml /ospool/images-scripts/
COPY --chmod=0755 update.py /ospool/images-scripts/
COPY --chmod=0755 startup.sh /bin/startup.sh

ENV CRON_EXPR="30 5 * * *"
ENV TIMEOUT="23h"

VOLUME ["/ospool/images"]

CMD ["/bin/startup.sh"]

