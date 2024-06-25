#!/bin/bash
set -e
# Use git diff in the glideinwms checkout to generate the patch
SITE_PACKAGES=$(python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')
pushd $SITE_PACKAGES/glideinwms
patch -p1 <<'__END_PATCH__'
diff --git a/creation/lib/cvWCreate.py b/creation/lib/cvWCreate.py
index f88353830..80e0c943a 100644
--- a/creation/lib/cvWCreate.py
+++ b/creation/lib/cvWCreate.py
@@ -210,7 +210,7 @@ def create_client_condor_config(config_fname, mapfile_fname, collector_nodes, cl
         fd.write("############################\n")

         fd.write("\n# Force GSI authentication\n")
-        fd.write("SEC_DEFAULT_AUTHENTICATION_METHODS = IDTOKENS, GSI\n")
+        fd.write("SEC_DEFAULT_AUTHENTICATION_METHODS = IDTOKENS, SSL\n")
         fd.write("SEC_DEFAULT_AUTHENTICATION = REQUIRED\n")

         fd.write("\n#################################\n")
@@ -224,7 +224,12 @@ def create_client_condor_config(config_fname, mapfile_fname, collector_nodes, cl
         fd.write("# I.e. we only talk to servers that have \n")
         fd.write("#  a DN mapped in our mapfile\n")
         for context in condorSecurity.CONDOR_CONTEXT_LIST:
-            fd.write("DENY_%s = anonymous@*\n" % context)
+            if context == "CLIENT":
+                # as we map SSL to anonymous, but want to allow
+                # anonymous clients, just put a placeholder for CLIENT
+                fd.write("DENY_%s = no-deny\n" % context)
+            else:
+                fd.write("DENY_%s = anonymous@*\n" % context)
         fd.write("\n")
         for context in condorSecurity.CONDOR_CONTEXT_LIST:
             fd.write("ALLOW_%s = *@*\n" % context)
__END_PATCH__
popd
