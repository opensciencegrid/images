# Specify the opensciencegrid/ospool-cm image tag
ARG BASE_OSG_SERIES=3.6
ARG BASE_YUM_REPO=release

FROM opensciencegrid/ospool-cm:$BASE_OSG_SERIES-$BASE_YUM_REPO

# has to be redefined for use in the RUN stages
ARG BASE_YUM_REPO

RUN dnf -y install \
      ganglia-gmond \
      ganglia-gmetad \
      ganglia-web \
      httpd \
      php-fpm \
    && \
    dnf -y clean all && \
    mkdir -p /run/php-fpm

COPY 05-gmetad.conf /etc/supervisord.d/
COPY 05-gmond.conf /etc/supervisord.d/
COPY 05-httpd.conf /etc/supervisord.d/
COPY 05-php-fpm.conf /etc/supervisord.d/
COPY gmetad.conf /etc/ganglia/
COPY 50-ganglia.conf /etc/condor/config.d/
COPY 50-ospool-config.sh /etc/osg/image-init.d/
COPY httpd-ganglia.conf /etc/httpd/conf.d/ganglia.conf


