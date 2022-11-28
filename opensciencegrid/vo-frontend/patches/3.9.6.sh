#!/bin/bash
set -e
# Use git diff in the glideinwms checkout to generate the patch
pushd /usr/lib/python3.6/site-packages/glideinwms
patch -p1 <<'__END_PATCH__'
diff --git a/frontend/glideinFrontendInterface.py b/frontend/glideinFrontendInterface.py
index b280452e..2624cf09 100644
--- a/frontend/glideinFrontendInterface.py
+++ b/frontend/glideinFrontendInterface.py
@@ -10,10 +10,6 @@
 # Description:
 #   This module implements the functions needed to advertize
 #   and get resources from the Collector
-#
-# Author:
-#   Igor Sfiligoi (Sept 15th 2006)
-#
 
 
 import calendar
@@ -362,7 +358,7 @@ class Credential:
 
     def getIdFilename(self):
         """
-        Get credential file used to generate the credential id
+        Get credential file (name, aka string) used to generate the credential id
         """
 
         # This checks seem hacky. Ideally checking against the credetnial type
@@ -375,6 +371,8 @@ class Credential:
             cred_file = self.key_fname
         elif self.pilot_fname:
             cred_file = self.pilot_fname
+        elif self.generator:
+            cred_file = self.generator
         return cred_file
 
     def create(self):
@@ -1198,24 +1196,8 @@ class MultiAdvertizeWork:
 
                 req_idle = 0
                 req_max_run = 0
-                if True:  # for historical reasons... to preserve indentation
-                    credential_el = credentials_with_requests[i]
-                    logSupport.log.debug("Checking Credential file %s ..." % (credential_el.filename))
-                    if credential_el.supports_auth_method("scitoken"):
-                        try:
-                            token_expired = token_util.token_str_expired(credential_el.generated_data)
-                        except AttributeError:
-                            token_expired = token_util.token_file_expired(credential_el.filename)
-                        if token_expired:
-                            logSupport.log.warning("Credential file %s is expired, skipping" % credential_el.filename)
-                            continue
-                    if credential_el.advertize == False:
-                        # We already determined it cannot be used
-                        # if hasattr(credential_el,'filename'):
-                        #    filestr=credential_el.filename
-                        # logSupport.log.warning("Credential file %s had some earlier problem in loading so not advertizing, skipping..."%(filestr))
-                        continue
 
+                # credential_el (Credebtial())
                 credential_el = credentials_with_requests[i]
                 logSupport.log.debug("Checking Credential file %s ..." % (credential_el.filename))
                 if credential_el.advertize == False:
@@ -1225,6 +1207,22 @@ class MultiAdvertizeWork:
                     # logSupport.log.warning("Credential file %s had some earlier problem in loading so not advertizing, skipping..."%(filestr))
                     continue
 
+                if credential_el.supports_auth_method("scitoken"):
+                    try:
+                        # try first for credential generator
+                        token_expired = token_util.token_str_expired(credential_el.generated_data)
+                    except AttributeError:
+                        # then try file stored credential
+                        token_expired = token_util.token_file_expired(credential_el.filename)
+                    if token_expired:
+                        logSupport.log.warning(
+                            "Credential file %s has expired scitoken, skipping" % credential_el.filename
+                        )
+                        continue
+                    glidein_params_to_encrypt["ScitokenId"] = file_id_cache.file_id(
+                        credential_el, credential_el.filename
+                    )
+
                 if params_obj.request_name in self.factory_constraint:
                     if (factory_auth != "Any") and (not credential_el.supports_auth_method(factory_auth)):
                         logSupport.log.warning(
__END_PATCH__
popd
