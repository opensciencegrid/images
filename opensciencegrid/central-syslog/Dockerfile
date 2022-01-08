ARG IMAGE_BASE_TAG=release

FROM hub.opensciencegrid.org/opensciencegrid/software-base:3.6-el8-$IMAGE_BASE_TAG

LABEL maintainer OSG Software <support@opensciencegrid.org>

RUN yum -y install rsyslog rsyslog-gnutls

ADD etc /etc

