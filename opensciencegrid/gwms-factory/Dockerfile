FROM opensciencegrid/software-base:3.6-el7-release
LABEL maintainer OSG Software <help@opensciencegrid.org>

# Create the frontend user with a fixed GID/UID
# This is important so that we can use the same IDs in the persistent volume used for
# the web-area
RUN groupadd -o -g 996 gfactory && useradd -o -u 996 -g 996 -s /bin/sh gfactory

RUN yum -y install glideinwms-factory vo-client git python3-PyYAML

ADD etc /etc
