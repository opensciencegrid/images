ARG BASE_YUM_REPO=release
ARG BASE_OSG_SERIES=3.6

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-el7-$BASE_YUM_REPO

LABEL maintainer OSG Software <help@opensciencegrid.org>

RUN yum -y --enablerepo=osg-upcoming install \
           condor \
           curl \
           git \
           python-devel \
           python-pip \
           python-setuptools \
           wget \
    && \
    yum clean all

COPY fifemon-condor-probe /fifemon

RUN pip install --upgrade setuptools==41.4.0 && \
    cd /fifemon && \
    python setup.py install
    
COPY fifemon.cfg-development /etc/fifemon.cfg-development
COPY fifemon.cfg-production /etc/fifemon.cfg-production
COPY 50-ospool.conf /etc/condor/config.d/50-ospool.conf

ADD image-config.d/*    /etc/osg/image-config.d/
ADD supervisor.d/*      /etc/supervisord.d/

