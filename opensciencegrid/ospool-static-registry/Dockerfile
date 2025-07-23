# Specify the opensciencegrid/software-base image tag
ARG BASE_OSG_SERIES=24
ARG BASE_YUM_REPO=release

FROM opensciencegrid/software-base:$BASE_OSG_SERIES-el8-$BASE_YUM_REPO AS builder

RUN yum install -y skopeo && \
    mkdir /var/lib/images

WORKDIR /var/lib/images
RUN mkdir -p \
  alpine \
  hello-world

RUN skopeo copy --format v2s2 --dest-compress docker://docker.io/alpine:latest      dir:alpine/latest
RUN skopeo copy --format v2s2 --dest-compress docker://docker.io/hello-world:latest dir:hello-world/latest

COPY static-container-registry.py /static-container-registry.py
RUN python3 /static-container-registry.py /var/lib/images > /static-container-registry.conf

##############################################################################
FROM nginx:stable-alpine

RUN sed -i \
        '/location \/ {/i include\ \/etc\/nginx\/static-container-registry.conf;' \
        /etc/nginx/conf.d/default.conf

COPY --from=builder /var/lib/images /var/lib/images
COPY --from=builder /static-container-registry.conf /etc/nginx
