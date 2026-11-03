FROM rockylinux/rockylinux:10

# dependency needed by OSG
RUN dnf install -y 'dnf-command(config-manager)' && \
    dnf config-manager --set-enabled crb && \
    yum clean all

# OSG RPMs
# osg-ca-certs must be recent enough for the current Let's Encrypt chains (YE1, ISRG Root YE)
RUN yum -y install https://repo.opensciencegrid.org/osg/25-main/osg-25-main-el10-release-latest.rpm && \
    yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-10.noarch.rpm && \
    yum -y install python3-pip less which && \
    yum -y install osg-ca-certs condor python3-condor && \
    yum clean all


RUN pip3 install --no-cache-dir kubernetes==37.0.1


# Tell condor to use osg-ca-certs
ADD 03_condor_sec.config /etc/condor/config.d/03_condor_sec.config

# configure python packages
ADD src /opt/provisioner/src

# Copy /etc/skel explicitly: when built under amd64 emulation (e.g. on an arm64 Mac), EL10's useradd
# leaves the home empty, and without ~/.bash_profile 'su -l' never reads the ~/.bashrc the setup scripts write
RUN useradd provisioner && cp -a /etc/skel/. /home/provisioner/ && chown -R provisioner: /home/provisioner && chown -R provisioner /opt/provisioner

RUN su provisioner -c '/usr/bin/ln -s /opt/provisioner/src /home/provisioner/src'

ADD provisioner_main.py /home/provisioner/provisioner_main.py
ADD provisioner_info.py /home/provisioner/provisioner_info.py
RUN chown provisioner /home/provisioner/provisioner_main.py; chmod a+x /home/provisioner/provisioner_info.py; chown provisioner /home/provisioner/provisioner_info.py

ADD setup_k8s_creds.sh /opt/provisioner/setup_k8s_creds.sh
ADD setup_htcondor_creds.sh /opt/provisioner/setup_htcondor_creds.sh
ADD provisioner_startup.sh /opt/provisioner/provisioner_startup.sh

#
# Requires env variables
# CONDOR_HOST
# K8S_NAMESPACE
# CVMFS_MOUNTS

#
# Optional env variable
# HTCONDOR_QUERY_INSECURE
#

CMD ["/opt/provisioner/provisioner_startup.sh"]

