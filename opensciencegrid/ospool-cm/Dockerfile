# Specify the opensciencegrid/software-base image tag
ARG BASE_OSG_SERIES=3.6
ARG BASE_YUM_REPO=release

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-el8-$BASE_YUM_REPO

# has to be redefined for use in the RUN stages
ARG BASE_YUM_REPO

RUN yum -y upgrade && \
    yum -y install \
      git \
      lsof \
      rrdtool \
      vim \
      wget \
    && \
    yum clean all

# Pull HTCondor from the proper repo. For "release" we need to use
# osg-upcoming-testing to meet the patch tuesday requirements.
RUN if [[ $BASE_YUM_REPO = release ]]; then \
      yum -y --enablerepo=osg-upcoming-testing install condor; \
    else \
      yum -y install condor; \
    fi

COPY condor_master_wrapper /usr/sbin/
RUN chmod 755 /usr/sbin/condor_master_wrapper

# Override the software-base supervisord.conf to throw away supervisord logs
COPY supervisord.conf /etc/supervisord.conf

COPY 10-htcondor.conf /etc/supervisord.d/

COPY ospool-overview /opt/ospool-overview

ADD healthy.sh /healthy.sh

