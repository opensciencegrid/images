FROM centos/systemd:latest
COPY supervisord.conf tmp/supervisord.conf
COPY fts-diff-4.0.1.sql usr/share/fts-mysql/fts-diff-4.0.1.sql 
COPY fts3config etc/fts3/fts3config
COPY fts-msg-monitoring.conf etc/fts3/fts-msg-monitoring.conf
COPY docker-entrypoint.sh tmp/docker-entrypoint.sh 
RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == \
systemd-tmpfiles-setup.service ] || rm -f $i; done); \
rm -f /lib/systemd/system/multi-user.target.wants/*;\
rm -f /etc/systemd/system/*.wants/*;\
rm -f /lib/systemd/system/local-fs.target.wants/*; \
rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
rm -f /lib/systemd/system/basic.target.wants/*;\
rm -f /lib/systemd/system/anaconda.target.wants/*;
VOLUME [ "/sys/fs/cgroup" ]
CMD ["/usr/sbin/init"]
RUN rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN rpm -Uvh https://repo.opensciencegrid.org/osg/3.4/osg-3.4-el7-release-latest.rpm
RUN yum install -y osg-ca-certs yum-plugin-priorities gfal2-all osg-gridftp gfal2-util fts-server fts-client fts-rest fts-monitoring fts-mysql fts-server-selinux fts-rest-selinux fts-monitoring-selinux fts-msg fts-infosys cronie crontabs supervisor
LABEL version="0.1"
LABEL description="This Docker image from the Enrico Fermi Institute contains resources for an FTS3 service. This image expects a mariaDB Container. Documentation forthcoming."
ENTRYPOINT sh tmp/docker-entrypoint.sh
