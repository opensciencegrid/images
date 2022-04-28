FROM python:3.8.5-alpine

WORKDIR /contact-sync

COPY contact_sync.py \
     status_api.py \
       ./

ADD https://raw.githubusercontent.com/opensciencegrid/topology/v1.17.1/src/topology_utils.py ./

# Files from ADD end up with 600
RUN chmod 755 *.py

RUN \ 
       pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir requests

#CMD python ./contact_sync.py --cert '/contact_sync/usercert.pem' --key '/contact_sync/userkey.pem' list-contacts  --type 'administrative'
