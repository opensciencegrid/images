FROM centos:centos7

LABEL maintainer OSG Software <help@opensciencegrid.org>

RUN yum -y install http://repo.opensciencegrid.org/osg/3.4/osg-3.4-el7-release-latest.rpm \
                   epel-release \
                   yum-plugin-priorities

RUN yum clean all && \
    yum update -y 

RUN yum install -y frontier-squid && \
    yum install -y supervisor

RUN yum clean all --enablerepo=* && rm -rf /var/cache/yum/


RUN systemctl enable frontier-squid

ADD sbin/* /usr/local/sbin/

ADD supervisord.conf /etc/
ADD supervisord.d/* /etc/supervisord.d/

EXPOSE 3128

CMD ["/usr/local/sbin/supervisord_startup.sh"]
