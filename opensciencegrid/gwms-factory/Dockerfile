ARG BASE_OS=el9
ARG BASE_OSG_SERIES=23
ARG BASE_YUM_REPO=release

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-$BASE_OS-$BASE_YUM_REPO
LABEL maintainer OSG Software <help@opensciencegrid.org>

# Previous build args went out of scope
ARG BASE_OS

# Create the condor and factory users with a fixed GID/UID
# This is important so that we can use the same IDs in persistent volumes
RUN groupadd -g 1000 condor && useradd -u 1000 -g condor -s /bin/sh condor
RUN groupadd -g 1001 gfactory && useradd -u 1001 -g gfactory -s /bin/sh gfactory

RUN    yum -y install \
         git \
         glideinwms-factory \
         msmtp \
         vo-client \
         vim-enhanced \
    && rm -rf /var/cache/yum/*

# Note: EL7 and EL8 PyYAML RPM version is too old to include yaml.FullLoader (v5.1+)
#       for glideinwms/lib/config_util.py
RUN if [[ ${BASE_OS} < 'el9' ]] ; then \
      pip3 install --upgrade --no-cache-dir PyYAML \
    ; fi

ADD etc /etc
ADD usr /usr
