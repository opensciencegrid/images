ARG BASE_OSG_SERIES=3.6
ARG BASE_YUM_REPO=release

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-al8-$BASE_YUM_REPO
# OSG kojid container
# Requires CAP_SYS_ADMIN for chroot(1), unshare(1), and mounting tmpfs

LABEL maintainer OSG Software <help@opensciencegrid.org>

RUN --mount=type=cache,target=/var/cache/dnf,sharing=locked \
 yum install -y --enablerepo=devops-itb 'koji-builder >= 1.21.1'

COPY kojid-supervisord.conf  /etc/supervisord.d/kojid.conf
COPY koji_ca_cert.crt  /etc/pki/tls/certs/koji_ca_cert.crt
RUN touch /var/log/kojid.log
COPY --chmod=0755 healthcheck /sbin/healthcheck
COPY --chmod=0755 cleanup /etc/cron.hourly
