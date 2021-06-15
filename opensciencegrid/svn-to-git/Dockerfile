FROM opensciencegrid/software-base:fresh
LABEL maintainer OSG Software <help@opensciencegrid.org>

# Install dependencies
# Install git from IUS (Rackspace) repo for a modern version (without SCL setup headache)
RUN \
     yum update -y \
  && yum install -y \
       epel-release \
       https://repo.ius.io/ius-release-el7.rpm \
  && yum install -y \
       git224 \
       git224-svn \
       subversion \
  && yum clean all && rm -rf /var/cache/yum/*

# Install gems and get SSH keys
RUN \
     ssh-keyscan github.com >> /etc/ssh/ssh_known_hosts

COPY svn-to-git.sh /usr/bin

CMD /usr/bin/svn-to-git.sh
