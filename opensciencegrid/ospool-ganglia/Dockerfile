# Specify the opensciencegrid/software-base image tag
ARG BASE_OSG_SERIES=23
ARG BASE_YUM_REPO=release

# has to be el8 for a working ganglia/php combination
FROM opensciencegrid/software-base:$BASE_OSG_SERIES-el8-$BASE_YUM_REPO

# has to be redefined for use in the RUN stages
ARG BASE_YUM_REPO

# has to be redefined for use in the RUN stages
ARG BASE_YUM_REPO

RUN dnf -y distro-sync && \
    dnf -y install \
      epel-release && \
    dnf -y install \
      bc \
      ganglia-gmetad \
      ganglia-gmond \
      ganglia-web \
      git \
      httpd \
      lsof \
      php-fpm \
      python3-pip \
      rrdtool \
      vim \
      wget \
      lrzsz \
    && \
    dnf -y clean all && \
    mkdir -p /run/php-fpm

# Pull HTCondor from the proper repo. For "release" we need to use
# osg-upcoming-testing to meet the patch tuesday requirements.
RUN if [[ $BASE_YUM_REPO = release ]]; then \
      dnf -y --enablerepo=osg-upcoming-testing install condor; \
    else \
      dnf -y install condor; \
    fi

COPY condor_master_wrapper /usr/sbin/
RUN chmod 755 /usr/sbin/condor_master_wrapper
COPY 10-htcondor.conf /etc/supervisord.d/

COPY 03-rrdcached.conf /etc/supervisord.d/
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


