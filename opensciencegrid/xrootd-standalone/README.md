Xrootd Standalone Docker Image [![Build Status](https://travis-ci.org/opensciencegrid/docker-xrootd-standalone.svg?branch=master)](https://travis-ci.org/opensciencegrid/docker-xrootd-standalone)
==============================

This image is based on the [osg-xrootd-standalone RPM](https://github.com/opensciencegrid/Software-Redhat/tree/trunk/osg-xrootd).

For more information for [Xrootd Standalone](https://opensciencegrid.org/docs/data/xrootd/install-standalone/)


Running a Container
-------------------

```
$ docker run --rm --publish <HOST PORT>:1094 \
             opensciencegrid/docker-xrootd-standalone:fresh
```

The `HOST PORT` is the port on your computer which will accept caching requests.  You may see some failures.  

Readying for Production
------------------------

Additional configuration is needed to make XrootD Standalone production-ready.

1. Add a persistant directory from which XrootD will serve its contents.

An example final `docker run` command:

```
$ docker run --rm --publish <HOST PORT>:1094 \
             --volume /baremetalPartition:/data
             opensciencegrid/docker-xrootd-standalone:fresh
```

1. Also needed is to create a configuration file and place it inside the container `/etc/xrootd/config.d/10-common-site-local.cfg` with the name of the resource that matches topology.

Create a file `10-my-site-variables.cfg:` with the following contents:
```
set resourcedir = /data
set rootdir = <TOPOLOGY RESOURCE NAME>
```

With this file you can run this command:
```
docker run --rm \
       --publish 1094:1094 \
       --volume 10-my-site-variables.cfg:/etc/xrootd/config.d/10-common-site-local.cfg \
       --name xrootd_standalone opensciencegrid/xrootd-standalone:stable &
```

