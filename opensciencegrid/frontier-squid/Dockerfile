FROM centos:7
MAINTAINER carcassi@umich.edu

RUN rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && \
    yum install -y yum-plugin-priorities && \
    rpm -Uvh http://mirror.grid.uchicago.edu/pub/osg/3.4/osg-3.4-el7-release-latest.rpm

RUN yum clean all && \
    yum update -y && \
    yum install -y frontier-squid && \
    yum install -y supervisor && \
    systemctl enable frontier-squid

ADD sbin/* /usr/local/sbin/

ADD supervisord.conf /etc/
ADD supervisord.d/* /etc/supervisord.d/

EXPOSE 3128

CMD ["/usr/local/sbin/supervisord_startup.sh"]
