ospool-static-registry
======================

This is a set of scripts to create a Docker-compatible read-only 'registry' that
can be served by a static Nginx HTTP server, without the need to run a
full-fledged registry solution.

This registry serves docker images used by the ospool singularity detection
scripts.

Heavily based on [NicolasT/static-container-registry](https://github.com/NicolasT/static-container-registry)

