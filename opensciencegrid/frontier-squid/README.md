Frontier Squid Container Image [![Build Status](https://github.com/opensciencegrid/docker-frontier-squid/workflows/dispatched%20build-docker-image/badge.svg)](https://github.com/opensciencegrid/docker-frontier-squid/actions?query=workflow%3A%22dispatched+build-docker-image%22)
==============================

A [Docker](https://hub.docker.com/r/opensciencegrid/frontier-squid) container image for
[Squid proxy server](http://www.squid-cache.org/) as packaged by [OSG](https://osg-htc.org/).
The image is built according to the
[OSG installation instructions](https://osg-htc.org/docs/data/frontier-squid/).

Usage
-----

To run with the defaults on docker or podman:

```bash
docker run --rm --name frontier-squid \
  -p 3128:3128 opensciencegrid/frontier-squid:24-release
```

Running docker or podman with a `-u` option to start as a non-root user
is also supported.

To run with the default settings on apptainer:

```bash
apptainer run --writable-tmpfs \
  -B /scratch/squid/cache:/var/cache/squid \
  -B /scratch/squid/log:/var/log/squid \
  docker://opensciencegrid/frontier-squid:24-release
```

Replace `/scratch/squid` with a path to wherever you have a filesystem
large enough to hold the squid cache and logs.

See [our documentation](https://osg-htc.org/technology/policy/container-release/#tags) for details of our docker
image tags.

Configuring Squid
-----------------

The recommended way to configure the squid in the container is by means of environment variables.
Three such variables are supported for simple installations:

Variable name       | Description                                                             | Defaults                                     |
---------------------|-------------------------------------------------------------------------|----------------------------------------------|
SQUID_IPRANGE       | Limits the incoming connections to the provided whitelist.     |By default only standard private network addresses are whitelisted. |
SQUID_CACHE_DISK    | Sets the cache_dir option which determines the disk size squid uses. Must be an integer value, and its unit is MBs. Note: The cache disk area is located at /var/cache/squid. | Defaults to 10000. |
SQUID_CACHE_MEM     | Sets the cache_mem option which regulates the size squid reserves for caching small objects in memory. Includes a space and unit, e.g. "MB". | Defaults to "128 MB". |

Additional configuration changes may be made by files in `/etc/squid/customize.d`.  See the documentation for that in [squid-customize.sh](squid-customize.sh).

Moreover, be aware that in order to preserve the cache between redeployments, you should map the following areas to persistent storage outside the container:

Mountpoint       | Description                                                          | Example docker mount               |
-----------------|----------------------------------------------------------------------|------------------------------------|
/var/cache/squid | This directory contains the cache for squid. See also SQUID_CACHE_DISK above. | -v /tmp/squid:/var/cache/squid |
/var/log/squid   | This directory contains the squid logs.                              | -v /tmp/log:/var/log/squid         |

For production deployments, OSG recommends allocating at least 50 to 100 GB (50000 to 100000 MB) to SQUID_CACHE_DISK.

For more details, see the [Frontier Squid documentation](https://osg-htc.org/docs/data/frontier-squid/#configuring-frontier-squid).


Multiple workers
----------------

If you define multiple workers in order to take advantage of multiple cores on a heavily loaded installation, be aware that for frontier-squid-6 (used in the 24-upcoming tag and in series 25 tags or later) you will need to configure rock cache.
That depends on a lot of RAM defined in $SQUID_CACHE_MEM for efficient operation and it allocates out of `/dev/shm` which by default in docker is very small.
To increase the size of `/dev/shm`, add the docker option `--shm-size`, for example `--shm-size=16g` for 16 Gigabytes.
If $SQUID_CACHE_MEM is defined to be too large to fit in `/dev/shm`, frontier-squid will automatically reduce the size.

If you want to avoid overriding the container's configuration environment variables which are used in `/etc/squid/customize.d/10-stdvars.awk`, there's no need to redefine `cache_mem` like the upstream documentation advises, and to set the cache type with the predefined location and size you can use
```
setoption("cache_dir", "rock '$SQUID_CACHE_DISK_LOCATION $SQUID_CACHE_DISK'")
```

Since at this point you need to pull together information from multiple sources to have a working configuration, here's an example configuration that puts it all together.  If you have a machine with 8 cores and 16G of RAM you could use a configuration like this, beginning with a file '20-frontier.awk' with these contents:
```
setoption("cache_dir", "rock '$SQUID_CACHE_DISK_LOCATION $SQUID_CACHE_DISK'")
setoption("maximum_object_size_in_memory", "1 GB")
setoption("workers", 6)
setoption("cpu_affinity_map", "process_numbers=1,2,3,4,5,6 cores=2,3,4,5,6,7")
```
Then start it with: 
```
docker run --rm --name frontier-squid -p 3128:3128 \
  -v ./20-frontier.awk:/etc/squid/customize.d/20-frontier.awk \
  --shm-size=14g -e SQUID_CACHE_MEM="12 GB" \
  -e SQUID_CACHE_DISK=50000 \
  --ulimit nofile=16384:16384 \
  opensciencegrid/frontier-squid:24-upcoming
```


Cache mem without multiple workers
----------------------------------

frontier-squid-6, as discussed in the multiple workers section above, allocates cache memory out of `/dev/shm`.
This happens even with the default one worker.
The default size of `/dev/shm` in docker is only 64 Megabytes, so even the default $SQUID_CACHE_MEM of 128 Megabytes doesn't fit.
This still works because frontier-squid reduces the size to fit, but especially if you choose to increase that size, pass a `--shm-size` option to docker that's at least 10% larger than $SQUID_CACHE_MEM.


Validate
--------

To validate your installation see the [OSG frontier-squid documentation](https://osg-htc.org/docs/data/frontier-squid/#validating-frontier-squid).
