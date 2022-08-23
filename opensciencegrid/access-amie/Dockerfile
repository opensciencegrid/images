ARG BASE_YUM_REPO=release
ARG BASE_OSG_SERIES=3.6

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-el8-$BASE_YUM_REPO

LABEL maintainer OSG Software <help@opensciencegrid.org>

RUN yum -y install \
           curl \
           python3-devel \
           python3-pip \
           vim \
           wget \
    && \
    yum clean all

RUN python3 -m pip install amieclient simplejson elasticsearch-dsl

# copy our app
WORKDIR /opt/access-amie
COPY . . 

# run the app
CMD ["python3", "/opt/access-amie/lib/Main.py"]

