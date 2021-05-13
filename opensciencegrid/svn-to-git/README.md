svn-to-git
==========

Mirror a repo from Subversion to Git using git-svn-mirror

# Environment variables

## Required

* `SVN_SRC` - Subversion source URL. Ex. `https://example.edu/svn/native/redhat`
* `GIT_DEST` - Destination git URL. Ex. `git@github.com:opensciencegrid/mirror.git`
* `AUTHORS_URL` - URL to retrieve the git-svn authors-file. Ex. `https://example.edu/authors.txt`
* `WORK_DIR` - Persistent working volume. Ex. `/data/mirror`

## Optional

* `GIT_SSH_COMMAND` - Allow SSH key path to be specified. Ex. `ssh -i /secrets/id_rsa`
* `SLEEP` - Sleep after container is complete for easy CronJob debugging. Ex. `15m`
