ARG BASE_OSG_SERIES=3.6
ARG BASE_YUM_REPO=release

FROM hub.opensciencegrid.org/opensciencegrid/software-base:$BASE_OSG_SERIES-el8-$BASE_YUM_REPO

LABEL maintainer OSG Software <help@opensciencegrid.org>

RUN    yum install -y xrootd \
                      inotify-tools \
                      # ^^^ Detect certificate changes
    && yum clean all \
    && rm -rf /var/cache/yum/*

ADD supervisord.d/*  /etc/supervisord.d/
ADD xrootd-redirector.cfg /etc/xrootd/

COPY cert-watch.sh xrd-certs-init.sh /usr/local/sbin/
RUN  chmod a+x /usr/local/sbin/*.sh

# Copy certs to /etc/grid-security/xrd on container startup
RUN ln -t /etc/osg/image-init.d -s /usr/local/sbin/xrd-certs-init.sh

