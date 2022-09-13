#!/bin/bash
set -e
# GIT: 72d0aafa Fixed python3 check return value in case of exception and minor pep8 improvements
# Use git diff in the glideinwms checkout to generate the patch
pushd /usr/lib/python3.6/site-packages/glideinwms
patch -p1 <<'__END_PATCH__'
diff --git a/frontend/glideinFrontendElement.py b/frontend/glideinFrontendElement.py
index 951710ed..52904755 100755
--- a/frontend/glideinFrontendElement.py
+++ b/frontend/glideinFrontendElement.py
@@ -879,13 +879,20 @@ class glideinFrontendElement:
                     gp_encrypt[entry_token_name] = ctkn
 
                 # now try to generate a credential using a generator plugin
-                stkn = self.generate_credential(self.elementDescript, glidein_el, self.group_name, trust_domain)
+                generator_name, stkn = self.generate_credential(
+                    self.elementDescript, glidein_el, self.group_name, trust_domain
+                )
 
                 # look for a local scitoken if no credential was generated
                 if not stkn:
                     stkn = self.get_scitoken(self.elementDescript, trust_domain)
 
                 if stkn:
+                    if generator_name:
+                        for cred_el in advertizer.descript_obj.x509_proxies_plugin.cred_list:
+                            if cred_el.filename == generator_name:
+                                cred_el.generated_data = stkn
+                                break
                     if token_util.token_str_expired(stkn):
                         logSupport.log.warning("SciToken is expired, not forwarding.")
                     else:
@@ -1065,13 +1072,13 @@ class glideinFrontendElement:
                             "factory": glidein_el["attrs"].get("AuthenticatedIdentity"),
                         }
                         stkn, _ = plugins[generator].get_credential(logSupport, group_name, entry, trust_domain)
-                        return stkn
+                        return cfname, stkn
                     except ModuleNotFoundError:
                         logSupport.log.warning(f"Failed to load credential generator plugin {generator}")
                     except Exception as e:  # catch any exception from the plugin to prevent the frontend from crashing
                         logSupport.log.warning(f"Failed to generate credential: {e}.")
 
-        return None
+        return None, None
 
     def refresh_entry_token(self, glidein_el):
         """
diff --git a/frontend/glideinFrontendInterface.py b/frontend/glideinFrontendInterface.py
index ed06c123..b280452e 100644
--- a/frontend/glideinFrontendInterface.py
+++ b/frontend/glideinFrontendInterface.py
@@ -863,7 +863,10 @@ class MultiAdvertizeWork:
             cred_el.loaded_data = []
             for cred_file in (cred_el.filename, cred_el.key_fname, cred_el.pilot_fname):
                 if cred_file:
-                    cred_data = cred_el.getString(cred_file)
+                    try:
+                        cred_data = cred_el.generated_data
+                    except AttributeError:
+                        cred_data = cred_el.getString(cred_file)
                     if cred_data:
                         cred_el.loaded_data.append((cred_file, cred_data))
                     else:
@@ -1199,7 +1202,11 @@ class MultiAdvertizeWork:
                     credential_el = credentials_with_requests[i]
                     logSupport.log.debug("Checking Credential file %s ..." % (credential_el.filename))
                     if credential_el.supports_auth_method("scitoken"):
-                        if token_util.token_file_expired(credential_el.filename):
+                        try:
+                            token_expired = token_util.token_str_expired(credential_el.generated_data)
+                        except AttributeError:
+                            token_expired = token_util.token_file_expired(credential_el.filename)
+                        if token_expired:
                             logSupport.log.warning("Credential file %s is expired, skipping" % credential_el.filename)
                             continue
                     if credential_el.advertize == False:
__END_PATCH__
popd
