# Specify the opensciencegrid/software-base image tag
ARG BASE_OSG_SERIES=3.5
ARG BASE_YUM_REPO=release

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-el7-$BASE_YUM_REPO

RUN yum -y upgrade && \
    yum -y install \
      condor \
      git \
      lsof \
      vim \
    && \
    yum clean all

COPY condor_master_wrapper /usr/sbin/
RUN chmod 755 /usr/sbin/condor_master_wrapper

# Override the software-base supervisord.conf to throw away supervisord logs
COPY supervisord.conf /etc/supervisord.conf

COPY 10-htcondor.conf /etc/supervisord.d/

