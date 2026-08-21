ARG BASE_OS=el9
ARG BASE_OSG_SERIES=25
ARG BASE_YUM_REPO=release

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-$BASE_OS-$BASE_YUM_REPO

RUN yum install -y rsync openssh-clients && \
yum clean all && \
rm -rf /var/cache/yum/

COPY 19_rsync_setup.sh /etc/osg/image-config.d/19_rsync_setup.sh
