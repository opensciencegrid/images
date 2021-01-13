FROM opensciencegrid/software-base:el8-fresh
# OSG kojid container
# Requires CAP_SYS_ADMIN for chroot

LABEL maintainer OSG Software <help@opensciencegrid.org>

RUN : \
&& yum install -y --enablerepo=devops-itb koji-builder \
&& yum clean all \
&& rm -rf /var/cache/yum/* \
&& :

COPY kojid-supervisord.conf  /etc/supervisord.d/kojid.conf
COPY koji_ca_cert.crt  /etc/pki/tls/certs/koji_ca_cert.crt
