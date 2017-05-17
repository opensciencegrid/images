
FROM opensciencegrid/osg-wn:3.3-el7

# install dependencies
RUN yum -y install --enablerepo=osg-contrib python-elasticsearch-dsl && \
  yum -y install https://github.com/apel/ssm/releases/download/2.1.7-1/apel-ssm-2.1.7-1.el7.noarch.rpm

COPY apel_report.py normal_hepspec /usr/libexec/apel/

