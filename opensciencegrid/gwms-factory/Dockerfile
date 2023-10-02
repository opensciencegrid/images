ARG BASE_OS=el9
ARG BASE_OSG_SERIES=23
ARG BASE_YUM_REPO=release

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-$BASE_OS-$BASE_YUM_REPO
LABEL maintainer OSG Software <help@opensciencegrid.org>

# Previous build args went out of scope
ARG BASE_OS

# Create the frontend user with a fixed GID/UID
# This is important so that we can use the same IDs in the persistent volume used for
# the web-area
RUN groupadd -o -g 996 gfactory && useradd -o -u 996 -g 996 -s /bin/sh gfactory

# Note: EL7 and EL8 PyYAML RPM version is too old to include yaml.FullLoader (v5.1+)
#       for glideinwms/lib/config_util.py
RUN    yum -y install \
         git \
         glideinwms-factory \
         msmtp \
         vo-client \
         vim-enhanced \
    && [[ ${BASE_OS} == 'el9' ]] \
       || pip3 install --no-cache-dir PyYAML \
    && rm -rf /var/cache/yum/*

ADD etc /etc
