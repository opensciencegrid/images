# Specify the opensciencegrid/software-base image tag
ARG BASE_OSG_SERIES=3.6
ARG BASE_YUM_REPO=release

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-el8-$BASE_YUM_REPO

LABEL maintainer OSG Software <help@opensciencegrid.org>

# Ensure that the 'condor' UID/GID matches across containers
# Using the RedHat assigned UID/GID for the condor user
RUN groupadd -g 64 -r condor
RUN useradd -r -g condor -d /var/lib/condor -s /sbin/nologin \
    -u 64 -c "Owner of HTCondor Daemons" condor

RUN \
 yum -y update  && \
 yum clean all  && \
 rm -rf /var/cache/yum/*

RUN \
 yum -y install osg-flock \
 openssh-clients && \
 yum clean all  && \
 rm -rf /var/cache/yum/*

# In the future, the condor RPMs will create these
RUN \
 install -m 0700 -o root -g root -d /etc/condor/passwords.d && \
 install -m 0700 -o condor -g condor -d /etc/condor/tokens.d

RUN \
 useradd submituser

RUN \
 install -m 0700 -o root -g root -d /root/config && \
 install -m 0700 -o root -g root -d /root/secrets

RUN touch /var/lock/subsys/gratia-probes-cron

COPY supervisord.conf /etc/supervisord.conf
COPY condor/*.conf /etc/condor/config.d/
COPY start.sh update-config update-secrets /
COPY fetch-crl.cron /etc/cron.d/fetch-crl

CMD ["/bin/bash", "-x", "/start.sh"]
