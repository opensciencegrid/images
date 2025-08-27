# Specify the opensciencegrid/software-base image tag
ARG BASE_OSG_SERIES=23
ARG BASE_YUM_REPO=testing
# The following could be overriden to "upcoming" (for example) to 
# install the application from upcoming instead of the base yum repo.
ARG APP_YUM_REPO=$BASE_YUM_REPO

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-el8-$BASE_YUM_REPO

LABEL maintainer OSG Software <help@opensciencegrid.org>

# Create the squid user with a fixed GID/UID; do this first, so that the Squid
# install does not do it.  Then do the installs.  All one instruction to reduce
# image size, etc.
RUN groupadd -o -g 10941 squid && \
    useradd -o -u 10941 -g 10941 -s /sbin/nologin -d /var/lib/squid squid && \
    yum update -y && \
    if [[ $APP_YUM_REPO == upcoming* ]]; then \
       yumrepo=""; \
    elif [[ $APP_YUM_REPO = release ]]; then \
       yumrepo=osg-upcoming; else \
       yumrepo=osg-upcoming-$APP_YUM_REPO; fi && \
    yum install -y \
                --disablerepo=$yumrepo \
                frontier-squid && \
    rm -rf /var/cache/yum/* && \
    mkdir /etc/squid/customize.d

RUN rpm --import https://packages.elastic.co/GPG-KEY-elasticsearch && \
    > /etc/yum.repos.d/elastic-7.x.repo \
        printf "%s\n" \
        "[elastic-7.x]" \
        "name=Elastic repository for 7.x packages" \
        "baseurl=https://artifacts.elastic.co/packages/7.x/yum" \
        "gpgcheck=1" \
        "gpgkey=https://artifacts.elastic.co/GPG-KEY-elasticsearch" \
        "enabled=1" \
        "autorefresh=1" \
        "type=rpm-md" && \
    yum install -y filebeat && \
    rm -rf /var/cache/yum/*

COPY start-frontier-squid.sh /usr/sbin/
COPY squid-customize.sh /etc/squid/customize.sh
COPY customize.d/* /etc/squid/customize.d/
COPY supervisor-frontier-squid.conf /etc/supervisord.d/40-frontier-squid.conf
COPY 10-chown-mount-points.sh /etc/osg/image-init.d/
# For OKD, which runs as non-root user and root group
RUN chgrp root /run/squid /etc/squid /var/cache/squid /var/log/squid
RUN chmod g+w /run/squid /etc/squid /var/cache/squid /var/log/squid
RUN chmod g+w /etc/cron.d /etc/cron.d/frontier-squid.cron

EXPOSE 3128

# These env variables can be changed in the container instance
# Set default values which should reflect what is in the RPM
ENV SQUID_IPRANGE="10.0.0.0/8 172.16.0.0/12 192.168.0.0/16 fc00::/7 fe80::/10"
ENV SQUID_CACHE_MEM="128 MB"
ENV SQUID_CACHE_DISK="10000"
ENV SQUID_CACHE_DISK_LOCATION="/var/cache/squid"
