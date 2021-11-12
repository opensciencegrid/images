FROM opensciencegrid/software-base:3.6-el7-release

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

