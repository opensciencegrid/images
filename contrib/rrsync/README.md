rsync-over-ssh sidecar
======================

Runs an sshd server intended to be deployed as a sidecar container in a
Kubernetes Pod, allowing external clients to write to a shared volume via
rsync over ssh.

To permit login, volume-mount an `authorized_keys` file into
`/root/.ssh/authorized_keys`.
Mount the target data volume into `/data`.

sshd is configured (see `10-rsync.conf`) to reject interactive shell
access: every session is forced through [`rrsync`](https://download.samba.org/pub/rsync/rrsync.1).
which restricts the client to rsync operations rooted at `/data` and
rejects anything else.

Example usage:

```
docker run --detach --name rrsync \
    -v ~/authorized_keys:/root/.ssh/authorized_keys \
    -v ~/mydata:/data \
    -p2222:22 rrsync
rsync -e "ssh -p 2222" myfile.txt root@localhost:/
```
