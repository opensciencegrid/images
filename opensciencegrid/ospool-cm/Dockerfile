# Specify the opensciencegrid/software-base image tag
ARG BASE_OSG_SERIES=3.6
ARG BASE_YUM_REPO=release

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-el8-$BASE_YUM_REPO

# base packages
RUN yum -y upgrade && \
    yum -y install \
      git \
      lsof \
      vim \
    && \
    yum clean all

# we want a newer HTCondor
RUN yum -y install --enablerepo=osg-upcoming-testing \
      condor \
    && \
    yum clean all

COPY condor_master_wrapper /usr/sbin/
RUN chmod 755 /usr/sbin/condor_master_wrapper

# Override the software-base supervisord.conf to throw away supervisord logs
COPY supervisord.conf /etc/supervisord.conf

COPY 10-htcondor.conf /etc/supervisord.d/

