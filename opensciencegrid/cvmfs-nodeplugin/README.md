# CVMFS DaemonSet for Kubernetes

[CVMFS](https://cernvm.cern.ch/fs/) provides a scalable, global, read-only
filesystem that is developed at CERN and used at many computing centers
to distribute software.  This repository contains manifests that can be
used by a Kubernetes administrator to make CVMFS mounts available to pods
running inside the cluster.

There are two pieces required to add support:

1. A CVMFS DaemonSet, a set of pods that runs on every host in the cluster.
   The CVMFS processes are run inside these pods and the FUSE filesystem
   mount is bind-mounted into the host filesystem.
2. A set of PersistentVolumes that permit bind-mounting the read-only host
   filesystem into user's pods. *This must be setup once per namespace*.

Both items require significant administrator privileges to setup as
they require the ability to view the host filesystem inside the container.

An arbitrary number of pods in the same namespace can mount a persistent
volume.  Accordingly, step 2 must be performed once for each namespace
where CVMFS is used.

CVMFS DaemonSet
---------------

The CVMFS DaemonSet is provided by the `cvmfs-daemonset` directory in
this repository.  It can be loaded with the following command:

```
kubectl apply -k cvmfs-daemonset
```

Note this additionally starts a Squid deployment to handle the caching
of HTTP requests to the wider system.

Persistent Volumes
------------------

The persistent volumes can be installed into the CVMFS namespace with the
following command:

```
kubectl apply -k cvmfs-pvcs
```

However, this only installs persistent volumes and the corresponding claims
into the `cvmfs` namespace.  You can utilize kustomize overlays to create these
claims across many namespaces.

Setup a directory with a `kustomization.yaml` for each namespace where you want
CVMFS:

```
/
  /namespace1/
    /namespace1/kustomization.yaml
  /namespace2/
    /namespace2/kustomization.yaml
```

The `kustomization.yaml` file for `namespace1` will look like this:

```
namespace: namespace1

namePrefix: namespace1-

bases:
  - ../cvmfs-pvcs
```

Then, CVMFS can be added to the namespace with the following command:

```
kubectl apply -k namespace1
```
