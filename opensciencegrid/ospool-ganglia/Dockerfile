# Specify the opensciencegrid/ospool-cm image tag
ARG BASE_OSG_SERIES=3.6
ARG BASE_YUM_REPO=release

FROM opensciencegrid/ospool-cm:$BASE_OSG_SERIES-$BASE_YUM_REPO

# has to be redefined for use in the RUN stages
ARG BASE_YUM_REPO

# Do not use OSG's rrdtool on EL7 -- it is too new and causes dependency failures
RUN . /etc/os-release && \
    if [ "$VERSION_ID" = "7*" ]; then \
        yum -y install rrdtool --disablerepo=osg\*; \
    fi && \
    yum -y install \
      ganglia-gmond \
      ganglia-gmetad \
      ganglia-web \
      httpd \
      php-fpm \
    && \
    yum -y clean all && \
    mkdir -p /run/php-fpm

COPY 05-gmetad.conf /etc/supervisord.d/
COPY 05-gmond.conf /etc/supervisord.d/
COPY 05-httpd.conf /etc/supervisord.d/
COPY 05-php-fpm.conf /etc/supervisord.d/

COPY gmetad.conf /etc/ganglia/

# Setup condor_ganglid for OSPool Monitoring
COPY 50-ganglia.conf /etc/condor/config.d/
# .... note: the below ganglia.d/ copy will also copy all subdirs
COPY ganglia.d/ /etc/condor/ganglia.d/
# Setup condor_ganglid for HTCondor CE Dashboard work
COPY 51-ganglia-ce-dashboards.conf /etc/condor/config.d/
# Make a ganglia view dashboard for CE charts
COPY view_chtc-spark.json /var/lib/ganglia-web/conf/
# Setup condor_gangliad for monitoring GPU usage in Icecube and IGWN pools
COPY 52-ganglia-icecube /etc/condor/config.d/
COPY 53-ganglia-igwn /etc/condor/config.d/

COPY 50-ospool-config.sh /etc/osg/image-init.d/

COPY 90-ospool-php.ini /etc/php.d/

COPY httpd-ganglia.conf /etc/httpd/conf.d/ganglia.conf

COPY index.php /var/www/html/

ADD ganglia-web-overrides /usr/share/ganglia

