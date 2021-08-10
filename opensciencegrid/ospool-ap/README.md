docker-access-point
===================

An Open Science Pool access point

Instructions
------------

### Docker

1.  Create a directory named `config/`, copy `ProbeConfig.template` into
    `config/ProbeConfig`, and fill out the `ProbeName` and `SiteName` fields.

2.  Create a directory named `secrets/`,
    and copy the access token for osg-flock.opensciencegrid.org to
    `secrets/token`.

3.  Start the container, bind mounting `config` to `/root/config`,
    and `secrets` to `/root/secrets`:

        docker run --rm -v config:/root/config:ro \
         -v secrets:/root/secrets:ro --name osg_submit_host \
         opensciencegrid/submit-host:stable

4.  Shell into the container, become `submituser`:

        docker exec -it osg_submit_host bash
        su - submituser

    You can launch jobs from there.


### Kubernetes

Same as above but use a ConfigMap and a Secret.
(Examples forthcoming.)
