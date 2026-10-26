#!/bin/bash
set -e
# Use git diff in the glideinwms checkout to generate the patch
SITE_PACKAGES=$(python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')
pushd $SITE_PACKAGES/glideinwms
patch -p1 <<'__END_PATCH__'
diff --git a/creation/lib/cvWCreate.py b/creation/lib/cvWCreate.py
index 04588c168..03c709474 100644
--- a/creation/lib/cvWCreate.py
+++ b/creation/lib/cvWCreate.py
@@ -200,7 +200,7 @@ def create_client_condor_config(config_fname, mapfile_fname, collector_nodes, cl
         fd.write("############################\n")
 
         fd.write("\n# Force GSI authentication\n")
-        fd.write("SEC_DEFAULT_AUTHENTICATION_METHODS = IDTOKENS, SSL, GSI\n")
+        fd.write("SEC_DEFAULT_AUTHENTICATION_METHODS = IDTOKENS, SSL\n")
         fd.write("SEC_DEFAULT_AUTHENTICATION = REQUIRED\n")
 
         fd.write("\n#################################\n")
__END_PATCH__
popd
