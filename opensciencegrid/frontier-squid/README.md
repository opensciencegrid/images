# slateci/osg-frontier-squid container image

A [Docker](https://www.docker.com/) container image for [Squid proxy server](http://www.squid-cache.org/) provided by [SLATE](http://slateci.org) as packaged by [OSG](https://www.opensciencegrid.org/). The image is built according to the [OSG installation instructions](http://opensciencegrid.github.io/docs/data/frontier-squid/).

# Usage

To run with the defaults:

```bash
docker run --rm --name --name osg-frontier-squid \
  -p 3128:3128 slateci/osg-frontier-squid
```

# Validate

To validate your installation:

```bash
> export http_proxy=http://localhost:3128
> wget -qdO/dev/null http://frontier.cern.ch 2>&1 | grep X-Cache
X-Cache: MISS from 797a56e426cf
> wget -qdO/dev/null http://frontier.cern.ch 2>&1 | grep X-Cache
X-Cache: HIT from 797a56e426cf
```

# Configuring squid

|   | Type | Description  | Example |
|---|---|---|---|
| /etc/squid/customize.sh | Conf file (VOLUME)  | One possible way to configure squid is by passing the customise.sh file.  | -v ~/customize.sh:/etc/squid/customize.sh  |
| /etc/squid/squid.conf  | Conf file (VOLUME)  | One possible way to configure squid is by passing directly squid.conf file.  | -v ~/squid.conf:/etc/squid/squid.conf  |
| /var/cache/squid  | Cache dir (VOLUME)  | This directory contains the cache for squid. If the directory is persistent, the cache will presist after a redeployment.  |   |
