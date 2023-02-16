
# GlideinWMS Factory docker image

This container is a work-in-progress for the GlideinWMS factory image.

To launch, one must mount in the glideinWMS.xml and provide a configuration
repository.  Here is the example invocation used by the developer:

```
podman run --rm
   -v $HOME/projects/containers/factory/tarballs/:/var/lib/gwms-factory/condor/
   -v $HOME/projects/osg-gfactory/OSG/glideinWMS.xml:/etc/gwms-factory/glideinWMS.xml.base
   --env GWMS_FACTORY_REPO_1="https://github.com/bbockelm/osg-gfactory"
   --env GWMS_FACTORY_BRANCH_1="gfactory_config"
   CONTAINER_NAME
```

