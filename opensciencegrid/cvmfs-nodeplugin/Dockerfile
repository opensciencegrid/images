FROM opensciencegrid/software-base:fresh

# OSG RPMs
RUN \
    yum -y install osg-oasis \
    && yum clean all

ENV MOUNT_REPOS="config-osg.opensciencegrid.org,oasis.opensciencegrid.org,connect.opensciencegrid.org,singularity.opensciencegrid.org,icecube.opensciencegrid.org"
ENV SQUID_URI="http://frontier-squid:3128"
ENV QUOTA_LIMIT="4000"

ADD wait-only.sh /usr/local/sbin/wait-only.sh
ADD mount-and-wait.sh /usr/local/sbin/mount-and-wait.sh
ADD unmount-and-terminate.sh /usr/local/sbin/unmount-and-terminate.sh
ADD force_unmount.sh /usr/local/sbin/force_unmount.sh

CMD ["/usr/local/sbin/mount-and-wait.sh"]

