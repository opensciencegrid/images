ARG BASE_YUM_REPO=release
ARG BASE_OSG_SERIES=3.6

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-el9-$BASE_YUM_REPO

LABEL maintainer OSG Software <help@opensciencegrid.org>

RUN yum -y install \
      vim && \
    yum -y clean all

ADD osgconnect-report /opt/osgconnect-report

RUN cd /opt/osgconnect-report && ./create-venv

ENTRYPOINT ["/opt/osgconnect-report/runme.sh"]


