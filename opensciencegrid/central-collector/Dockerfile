ARG BASE_OSG_SERIES=3.6
ARG BASE_YUM_REPO=testing

FROM opensciencegrid/software-base:${BASE_OSG_SERIES}-el8-${BASE_YUM_REPO}
LABEL maintainer "OSG Software <help@opensciencegrid.org>"

# Previous args have gone out of scope
ARG BASE_OSG_SERIES=3.6
ARG BASE_YUM_REPO=testing

RUN    yum module enable -y mod_auth_openidc \
    && yum install -y htcondor-ce-collector \
                      htcondor-ce-view \
                      mod_ssl \
                      # ^^^ Doing SSL termination in the pod
                      perl-LWP-Protocol-https \
                      # ^^^ for fetch-crl, in the rare case that the CA forces HTTPS
                      mod_auth_openidc \
                      # ^^^ Install mod_auth_openidc from module
                      inotify-tools \
                      # ^^^ Detect certificate changes and reload httpd
    && yum clean all \
    && rm -rf /var/cache/yum/

# Create home directory for registry user
RUN mkdir /var/lib/condor-ce/webapp

COPY etc/supervisord.d/*      /etc/supervisord.d/
COPY etc/condor-ce/config.d/* /etc/condor-ce/config.d/
COPY etc/httpd/conf.d/*       /etc/httpd/conf.d/
COPY etc/osg/image-init.d/*   /etc/osg/image-init.d/
COPY auto-reload.sh           /usr/local/sbin/

RUN  chmod a+x /usr/local/sbin/auto-reload.sh
