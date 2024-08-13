ARG BASE_OSG_SERIES=24
ARG BASE_YUM_REPO=development

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-$BASE_OS-$BASE_YUM_REPO

# Previous instance has gone out of scope
ARG BASE_OSG_SERIES=24
ARG BASE_YUM_REPO=development

LABEL maintainer OSG Software <help@osg-htc.org>

RUN yum install -y git perl make cpan && \
    yum clean all && \
    rm -rf /var/cache/yum/* &&\
    mkdir /root/st &&\
    cd /root/st &&\
    git clone https://github.com/cern-mig/stompclt.git &&\
    cd stompclt &&\
    perl Makefile.PL &&\
    make &&\
    make install


