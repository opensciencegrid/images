ARG BASE_OSG_SERIES=3.6

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-al8-release
LABEL maintainer OSG Software <help@opensciencegrid.org>

# Install dependencies
RUN \
     yum update -y \
  && yum install -y \
       epel-release \
  && yum install -y \
       git \
       git-svn \
       subversion \
  && yum clean all && rm -rf /var/cache/yum/*

# Install gems and get SSH keys
RUN \
     ssh-keyscan github.com >> /etc/ssh/ssh_known_hosts

COPY svn-to-git.sh /usr/bin

CMD /usr/bin/svn-to-git.sh
