ARG BASE_OSG_SERIES=3.6
ARG BASE_YUM_REPO=release

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-al8-$BASE_YUM_REPO
# OSG kojid container
# Requires CAP_SYS_ADMIN for chroot(1), unshare(1), and mounting tmpfs

LABEL maintainer OSG Software <help@opensciencegrid.org>

RUN --mount=type=cache,target=/var/cache/dnf,sharing=locked \
 if [[ $BASE_OSG_SERIES = 3.6 ]]; then \
   yum install -y --enablerepo=devops-itb 'koji-builder >= 1.21.1'; \
 else \
   yum install -y --enablerepo=osg-internal-development 'koji-builder'; \
 fi

COPY kojid-supervisord.conf  /etc/supervisord.d/kojid.conf
COPY koji_ca_cert.crt  /etc/pki/tls/certs/koji_ca_cert.crt
COPY --chmod=0755 create-config.sh /etc/osg/image-init.d/create-config.sh
RUN touch /var/log/kojid.log
COPY --chmod=0755 healthcheck /sbin/healthcheck
COPY --chmod=0755 cleanup /etc/cron.hourly

# Required environment variables
# ------------------------------
# The hostname of the koji-hub XMLRPC server
ENV KOJI_HUB=
# The username of the kojid; needs to match the commonName of the cert/key
ENV KOJID_USER=
# Optional environment variables
# ------------------------------
# Maximum jobs to run at one time
ENV KOJID_MAXJOBS=10
# Minimum free megabytes of disk before starting a new job
ENV KOJID_MINSPACE=4096
# Seconds before killing possibly hung rpm build
ENV KOJID_RPMBUILD_TIMEOUT=43200
# Work directory to do builds in
ENV KOJID_WORKDIR=/var/lib/koji
# SSL cert/key file for authentication; the CN must match KOJID_USER
ENV KOJID_CERTKEY=/etc/pki/tls/private/kojid.pem
