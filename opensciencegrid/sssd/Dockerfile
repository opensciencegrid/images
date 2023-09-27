ARG BASE_OS=el9
ARG BASE_OSG_SERIES=23
ARG BASE_YUM_REPO=release

# Run sssd via supervisord.
#
# Containers must populate /etc/sssd with configuration for the daemon.
# Files must be readable only by root.

FROM hub.opensciencegrid.org/opensciencegrid/software-base:$BASE_OSG_SERIES-$BASE_OS-$BASE_YUM_REPO

# In order to accommodate the sharing of sssd's "pipes" directory, we
# create the sssd user and group with explicit IDs rather than allowing
# packages to select arbitrary IDs.

RUN groupadd -r -g 990 sssd \
    && useradd -r -g sssd -u 990 -d / -s /usr/sbin/nologin -c "System user for sssd" sssd \
    #
    && yum update -y \
    && yum install -y sssd \
    && yum clean all \
    && rm -rf /var/cache/yum/

COPY etc /etc/
