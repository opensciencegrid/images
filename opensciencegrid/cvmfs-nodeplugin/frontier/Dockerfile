FROM centos:centos7

RUN yum -y install https://repo.opensciencegrid.org/osg/3.4/osg-3.4-el7-release-latest.rpm && \
    yum -y install epel-release \
                   yum-plugin-priorities && \
    yum -y install  \
                   redhat-lsb-core && \
    yum -y install frontier-squid && \
    yum -y install supervisor

RUN yum clean all

RUN mkdir -p /var/log/supervisor
ADD supervisord.conf /etc/supervisord.conf

ADD dummy_pod_init.sh /usr/bin/pod_init.sh
ADD supervisord_startup.sh /usr/bin/supervisord_startup.sh

CMD ["/usr/bin/supervisord_startup.sh"]

