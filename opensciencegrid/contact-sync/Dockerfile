FROM python:3.8.5-alpine

WORKDIR /contact-sync

COPY contact_sync.py ./ 
COPY status_api.py ./
COPY topology_utils.py ./

RUN \ 
    pip3 install --upgrade pip \
    && pip3 install requests
    

#CMD python ./contact_sync.py --cert '/contact_sync/usercert.pem' --key '/contact_sync/userkey.pem' list-contacts  --type 'administrative'
