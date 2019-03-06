FROM centos:centos7

LABEL maintainer OSG Software <help@opensciencegrid.org>

# Create the squid user with a fixed GID/UID
RUN groupadd -o -g 10941 squid
RUN useradd -o -u 10941 -g 10941 -s /sbin/nologin -d /var/lib/squid squid


RUN yum -y install http://repo.opensciencegrid.org/osg/3.4/osg-3.4-el7-release-latest.rpm \
                   epel-release \
                   yum-plugin-priorities

RUN yum clean all && \
    yum update -y 

RUN yum install -y frontier-squid && \
    yum install -y supervisor

RUN yum clean all --enablerepo=* && rm -rf /var/cache/yum/

ADD sbin/* /usr/local/sbin/
ADD squid/* /etc/squid/

ADD supervisord.conf /etc/
ADD supervisord.d/* /etc/supervisord.d/
RUN mkdir -p /var/log/supervisor

EXPOSE 3128

CMD ["/usr/local/sbin/supervisord_startup.sh"]
