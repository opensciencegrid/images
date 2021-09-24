FROM opensciencegrid/software-base:3.6-el8-release
# OSG kojid container
# Requires CAP_SYS_ADMIN for chroot(1), unshare(1), and mounting tmpfs

LABEL maintainer OSG Software <help@opensciencegrid.org>

RUN : \
&& yum install -y --enablerepo=devops-itb koji-builder \
&& yum clean all \
&& rm -rf /var/cache/yum/* \
&& :

COPY kojid-supervisord.conf  /etc/supervisord.d/kojid.conf
COPY koji_ca_cert.crt  /etc/pki/tls/certs/koji_ca_cert.crt
RUN touch /var/log/kojid.log
COPY healthcheck /sbin/healthcheck
RUN chmod +x /sbin/healthcheck
COPY cleanup /etc/cron.hourly
RUN chmod +x /etc/cron.hourly/cleanup
