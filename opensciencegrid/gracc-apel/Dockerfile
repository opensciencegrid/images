
FROM opensciencegrid/osg-wn:3.3-el7

# install dependencies
RUN rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && \
  yum -y install yum-plugin-priorities && \
  rpm -Uvh https://repo.grid.iu.edu/osg/3.3/osg-3.3-el7-release-latest.rpm && \
  yum -y install --enablerepo=osg-contrib python-elasticsearch-dsl && \
  yum -y install https://github.com/apel/ssm/releases/download/2.1.7-1/apel-ssm-2.1.7-1.el7.noarch.rpm && \
  yum -y install openssh-clients

COPY apel_report.py normal_hepspec /usr/libexec/apel/

