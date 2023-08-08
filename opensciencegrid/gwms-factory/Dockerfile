FROM opensciencegrid/software-base:3.6-el7-release
LABEL maintainer OSG Software <help@opensciencegrid.org>

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
    && pip3 install --no-cache-dir PyYAML \
    && rm -rf /var/cache/yum/*

ADD etc /etc
ADD usr /usr
