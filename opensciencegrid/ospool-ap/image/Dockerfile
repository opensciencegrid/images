FROM opensciencegrid/software-base:fresh

RUN \
 yum -y update  && \
 yum -y install --enablerepo=osg-upcoming-rolling osg-flock  && \
 yum clean all  && \
 rm -rf /var/cache/*/*

# Create passwords directories for token or pool password auth.
#
# Only root needs to know the pool password but other condor daemons
# need access to the tokens.
#
# In the future, the RPMs will take care of this step.
RUN \
 install -m 0700 -o root -g root -d /etc/condor/passwords.d && \
 install -m 0700 -o condor -g condor -d /etc/condor/tokens.d

RUN \
 useradd submituser

COPY supervisord.conf /etc/supervisord.conf
COPY condor/*.conf /etc/condor/config.d/
COPY start.sh update-config update-secrets /

CMD ["/bin/bash", "-x", "/start.sh"]
