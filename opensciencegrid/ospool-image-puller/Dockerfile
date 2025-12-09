FROM almalinux:9

LABEL maintainer "OSG Software <help@osg-htc.org>"

RUN --mount=type=cache,id=dnf-el9,target=/var/cache/dnf,sharing=locked \
    dnf -y install crontabs cronie epel-release /usr/sbin/runuser procps-ng && \
    crb enable && \
    dnf -y install apptainer python3-pyyaml && \
    install -d /ospool/images-scripts && \
    # The home dir of the 'images' user will be under /var/home; \
    # this user will be created at startup with the UID specified by IMAGES_UID. \
    install -d /var/home

COPY --chmod=0644 images.yaml /ospool/images-scripts/
COPY --chmod=0755 update.py /ospool/images-scripts/
COPY --chmod=0755 startup.sh /bin/startup.sh

ENV CRON_EXPR="30 5 * * *"
ENV TIMEOUT="23h"
ENV IMAGES_UID="1000"
ENV KEEP_DAYS=10

VOLUME ["/ospool/images"]

CMD ["/bin/startup.sh"]
