rsyncd server
=============

Runs an rsync daemon that listens on port 873.  The default config serves,
read only, whatever is mounted into `/data`.  To override, mount a different
config into `/etc/rsyncd.conf`; see the `rsyncd-example.conf` file for
an example.

Example usage:

```
docker run --detach --name rsync -v ~/mydata:/data -p8873:873 rsync
rsync --port 8873 localhost::
rsync --port 8873 localhost::data
```