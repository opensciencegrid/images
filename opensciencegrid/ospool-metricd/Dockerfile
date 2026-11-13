# Specify the opensciencegrid/software-base image tag
ARG BASE_OS=el9
ARG BASE_OSG_SERIES=26
ARG BASE_YUM_REPO=release

# has to be el8 for a working ganglia/php combination
FROM opensciencegrid/software-base:$BASE_OSG_SERIES-$BASE_OS-$BASE_YUM_REPO

# has to be redefined for use in the RUN stages
ARG BASE_YUM_REPO

RUN dnf -y install \
      bc \
      git \
      vim \
      wget \
    && \
    dnf -y clean all

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

COPY 50-ospool-config.sh /etc/osg/image-init.d/

COPY condor/config.d/* /etc/condor/config.d/
COPY condor/metrics.d/* /etc/condor/metrics.d/

