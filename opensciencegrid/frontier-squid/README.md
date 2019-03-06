Frontier Squid Container Image [![Build Status](https://travis-ci.org/opensciencegrid/docker-frontier-squid.svg?branch=master)](https://travis-ci.org/opensciencegrid/docker-frontier-squid)
==============================

A [Docker](https://hub.docker.com/r/opensciencegrid/frontier-squid) container image for
[Squid proxy server](http://www.squid-cache.org/) as packaged by [OSG](https://www.opensciencegrid.org/).
The image is built according to the
[OSG installation instructions](http://opensciencegrid.github.io/docs/data/frontier-squid/).

Usage
-----

To run with the defaults:

```bash
docker run --rm --name osg-frontier-squid \
  -p 3128:3128 opensciencegrid/osg-frontier-squid
```

Configuring Squid
-----------------

The recommended way to configure the squid in the container is by means of environment variables.
Three such variables are supported:
* SQUID_IPRANGE - Limits the incoming connections to the provided whitelist. By default only standard private network addresses are whitelisted.
* SQUID_CACHE_DISK - Sets the cache_dir option which determines the disk size squid uses. Must be an integer value, and its unit is MBs. Defaults to 10000.
                     Note: The cache are is located at /var/cache/squid.
* SQUID_CACHE_MEM - Sets the cache_mem option which regulates the size squid reserves for caching small objects in memory. Defaults to "128 MB".

For more details, see the [squid official page](https://twiki.cern.ch/twiki/bin/view/Frontier/InstallSquid#Configuration).


Validate
--------

To validate your installation:

```bash
> export http_proxy=http://localhost:3128
> wget -qdO/dev/null http://frontier.cern.ch 2>&1 | grep X-Cache
X-Cache: MISS from 797a56e426cf
> wget -qdO/dev/null http://frontier.cern.ch 2>&1 | grep X-Cache
X-Cache: HIT from 797a56e426cf
```
