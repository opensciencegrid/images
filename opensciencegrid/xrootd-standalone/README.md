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

1. You might also want to control certains part of `/data` that are served through Xrootd. YOu can do that by creating a file `90-my-paths.cfg` and mounting it inside the container at `/etc/xrootd/config.d/90-osg-standalone-paths.cfg`. This is done via the [export directive](https://xrootd.slac.stanford.edu/doc/dev49/ofs_config.htm#_Toc522916544). An example file in which only files that start with `/mc` and `/data` will be exported would look like this:

```
all.export /mc
all.export /data
```

Then you would start your container like:

```
docker run --rm \
       --publish 1094:1094 \
       --volume 10-my-site-variables.cfg:/etc/xrootd/config.d/10-common-site-local.cfg \
       --volume 90-my-paths.cfg:/etc/xrootd/config.d/90-osg-standalone-paths.cf
       --name xrootd_standalone opensciencegrid/xrootd-standalone:stable &
```

1. For fine grained control of who has access to what you can also mount an [XrootD authfil](https://opensciencegrid.org/docs/data/xrootd/xrootd-authorization/)


Then run docker with:

```
docker run --rm \
       --publish 1094:1094 \
       --volume 10-my-site-variables.cfg:/etc/xrootd/config.d/10-common-site-local.cfg \
       --volume my_auth_file:/etc/xrootd/auth_file \
       --volume 90-my-paths.cfg:/etc/xrootd/config.d/90-osg-standalone-paths.cfg \
       --name xrootd_standalone opensciencegrid/xrootd-standalone:stable &
```

1. IF you want to do specific mappings of X509 DN to linux users or VOMS extension to linux users in the container you can create grid mpa files and voms-map-files and mount them like this:


```
"/myfavvo/" fav1
```

or specific users via gridmap file like:

```
"/TheDNofMyFavUser" favuser
```

And then moun them inside the container like this:

```
docker run --rm \
       --publish 1094:1094 \
       --volume 10-my-site-variables.cfg:/etc/xrootd/config.d/10-common-site-local.cfg \
       --volume	my_auth_file:/etc/xrootd/auth_file \
       --volume 90-my-paths.cfg:/etc/xrootd/config.d/90-osg-standalone-paths.cfg \
       --volume mygridmapfile:/etc/grid-security/grid-mapfile \
       --volume vomsmapfile:/etc/grid-security/voms-map-file \
       --name xrootd_standalone opensciencegrid/xrootd-standalone:stable &
```