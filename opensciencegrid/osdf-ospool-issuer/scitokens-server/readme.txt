Author: Jeff Gaynor
Created: 2021-08-20T11:12:15.435Z

Originally part of the scitokens/lightweight-issuer project.

This directory has the installation layout and files for the docker image.

╔══════════════════════════════════════════════════════════════════════════╗
║ NOTE: The permissions for this directory should be restricted to exactly ║
║ owner - root                                                             ║
║ group - tomcat                                                           ║
╚══════════════════════════════════════════════════════════════════════════╝

If the group is not tomcat, then tomcat cannot access anything in it.


Top level for the install is:

/opt/scitokens-server

All files below are relative to that.

web.xml = the web.xml file that should be deployed with this, overwriting the
          supplied web in the war. This contains the pointer to the configuration
          and configuring Tomcat as a standalone service.

    etc = configuration files.
          server-config.xml = the configuration for the OA4MP server.
          keys.jwk - generated JSON web keys

    log = log files, if logging is enabled.

    var = directory for things that vary.
         - storage
            -file_store = file store for OA4MP
         - qdl
            -scripts = mounted scripts directory for QDL (OA4MP's policy language).

