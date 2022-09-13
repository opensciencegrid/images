#!/bin/bash
set -e
# GIT: 2331f4b8 Ready for release v3_9_4
# Use git diff in the glideinwms checkout to generate the patch
pushd /usr/lib/python3.6/site-packages/glideinwms
patch -p1 <<'__END_PATCH__'
 creation/lib/cvWCreate.py          |   4 +-
 frontend/glideinFrontendElement.py | 106 +++++++++++++++++++++++++------------
 frontend/glideinFrontendLib.py     |   9 +++-
 3 files changed, 83 insertions(+), 36 deletions(-)

diff --git a/creation/lib/cvWCreate.py b/creation/lib/cvWCreate.py
index 00c8efd9..38f2c2a3 100644
--- a/creation/lib/cvWCreate.py
+++ b/creation/lib/cvWCreate.py
@@ -196,7 +196,9 @@ def filter_unwanted_config_attrs(attrs):
         unwanted_attrs.append('TOOL.SEC_%s_INTEGRITY' % context)
 
         # Keep default setting for following
-        if context!="DEFAULT":
+        # Exclude CLIENT as those settings are used to query schedds
+        # and some pools use non-authenticated queries
+        if context not in ["DEFAULT", "CLIENT"]:
             unwanted_attrs.append('SEC_%s_AUTHENTICATION' % context)
             unwanted_attrs.append('SEC_%s_AUTHENTICATION_METHODS' % context)
             unwanted_attrs.append('SEC_%s_INTEGRITY' % context)
diff --git a/frontend/glideinFrontendElement.py b/frontend/glideinFrontendElement.py
index 64acd9e1..912fad63 100755
--- a/frontend/glideinFrontendElement.py
+++ b/frontend/glideinFrontendElement.py
@@ -809,40 +809,12 @@ class glideinFrontendElement:
                     logSupport.log.debug("found condor token: %s" % entry_token_name)
                     gp_encrypt[entry_token_name] = ctkn
                 # now see if theres a scitoken for this site
-                scitoken_fullpath = ''
-                cred_type_data = self.elementDescript.element_data.get('ProxyTypes')
-                trust_domain_data = self.elementDescript.element_data.get('ProxyTrustDomains')
-                if not cred_type_data:
-                    cred_type_data = self.elementDescript.frontend_data.get('ProxyTypes')
-                if not trust_domain_data:
-                    trust_domain_data = self.elementDescript.frontend_data.get('ProxyTrustDomains')
-                if trust_domain_data and cred_type_data:
-                    cred_type_map = eval(cred_type_data)
-                    trust_domain_map = eval(trust_domain_data)
-                    for cfname in cred_type_map:
-                        if cred_type_map[cfname] == 'scitoken':
-                            if trust_domain_map[cfname] == trust_domain:
-                                scitoken_fullpath = cfname
-                    
-                if os.path.exists(scitoken_fullpath):
-                    try:
-                        logSupport.log.info('found scitoken %s' % scitoken_fullpath)
-                        with open(scitoken_fullpath,'r') as fbuf:
-                            for line in fbuf:
-                                stkn += line
-                        stkn = stkn.strip()
-
-                        if stkn:
-                            if token_util.token_str_expired(stkn):
-                                logSupport.log.warning('%s is expired, not forwarding' % scitoken_fullpath)
-                            else:
-                               gp_encrypt['frontend_scitoken'] =  stkn
-                    except Exception as err:
-                        logSupport.log.exception("failed to read scitoken: %s" % err)
-
+                stkn = self.refresh_entry_scitoken(glidein_el)
+                if stkn:
+                    gp_encrypt['frontend_scitoken'] =  stkn
 
                 # now advertise
-                logSupport.log.info('advertising tokens %s' % gp_encrypt.keys())
+                logSupport.log.debug('advertising tokens %s' % gp_encrypt.keys())
                 advertizer.add(factory_pool_node,
                            request_name, request_name,
                            glidein_min_idle,
@@ -910,6 +883,73 @@ class glideinFrontendElement:
 
         return
 
+
+    scitoken_allow_last_read = 0
+    scitoken_allow = []
+    def scitoken_ok(self, gatekeeper):
+        """
+            check the resource name against our list of tested scitoken sites
+        """
+        now = time.time()
+        if self.scitoken_allow_last_read is None or self.scitoken_allow_last_read < (now - 300):
+            logSupport.log.debug("Re-reading /var/lib/gwms-frontend/web-area/scitoken-testing/allow.txt")
+            self.scitoken_allow_last_read = now
+            with open('/var/lib/gwms-frontend/web-area/scitoken-testing/allow.txt', 'r') as f:
+                self.scitoken_allow = [line.strip() for line in f]
+
+        gk_simple = re.sub(' .*', '', gatekeeper)
+        return (gk_simple in self.scitoken_allow)
+
+
+    def refresh_entry_scitoken(self, glidein_el):
+        """
+            create or update a scitoken for an entry point
+            params:  glidein_el: a glidein element data structure
+            returns:  jwt encoded token on success
+                      None on failure
+        """
+        tkn_file = ''
+        tkn_str = ''
+        tmpnm = ''
+        logSupport.log.debug("Checking for scitoken refresh of %s." % glidein_el['attrs'].get('EntryName', '(unknown)'))
+        try:
+            # create a condor token named for entry point site name
+            glidein_site = glidein_el['attrs']['GLIDEIN_Site']; entry_name = glidein_el['attrs']['EntryName']
+            gatekeeper = glidein_el['attrs'].get('GLIDEIN_Gatekeeper')
+            audience = None
+            if gatekeeper:
+                audience = gatekeeper.split()[-1]
+            tkn_dir = "/var/lib/gwms-frontend/tokens.d"
+            if not os.path.exists(tkn_dir):
+                os.mkdir(tkn_dir,0o700)
+            tkn_file = tkn_dir + '/' + self.group_name + "." +  entry_name + ".scitoken"
+            one_hr = 3600
+            tkn_age = sys.maxsize
+            if os.path.exists(tkn_file):
+                tkn_age = time.time() - os.stat(tkn_file).st_mtime
+            if tkn_age > one_hr:
+                (fd, tmpnm) = tempfile.mkstemp()
+                cmd = "/usr/sbin/frontend_scitoken %s %s %s" % (audience, glidein_site, self.group_name)
+                tkn_str = subprocessSupport.iexe_cmd(cmd)
+                os.write(fd, tkn_str.encode('utf-8'))
+                os.close(fd)
+                shutil.move(tmpnm, tkn_file)
+                os.chmod(tkn_file, 0o600)
+                logSupport.log.debug("created token %s" % tkn_file)
+            elif os.path.exists(tkn_file):
+                with open(tkn_file, 'r') as fbuf:
+                    for line in fbuf:
+                        tkn_str += line
+        except Exception as err:
+                logSupport.log.warning('failed to create %s' % tkn_file)
+                for i in sys.exc_info():
+                    logSupport.log.warning('%s' % i)
+        finally:
+                if os.path.exists(tmpnm):
+                    os.remove(tmpnm)
+        return tkn_str
+
+
     def refresh_entry_token(self, glidein_el):
         """
             create or update a condor token for an entry point
@@ -980,7 +1020,7 @@ class glideinFrontendElement:
                     os.close(fd)
                     shutil.move(tmpnm, tkn_file)
                     chmod(tkn_file, 0o600)
-                    logSupport.log.info("created token %s" % tkn_file)
+                    logSupport.log.debug("created token %s" % tkn_file)
                 elif os.path.exists(tkn_file):
                     with open(tkn_file, 'r') as fbuf:
                         for line in fbuf:
diff --git a/frontend/glideinFrontendLib.py b/frontend/glideinFrontendLib.py
index 989f1125..65127804 100644
--- a/frontend/glideinFrontendLib.py
+++ b/frontend/glideinFrontendLib.py
@@ -1165,8 +1165,13 @@ def getCondorQConstrained(schedd_names, type_constraint, constraint=None, format
             logSupport.log.exception("Condor Error. Failed to talk to schedd: ")
             # If schedd not found it is equivalent to no jobs in the queue
             continue
-        except RuntimeError:
-            logSupport.log.exception("Runtime Error. Failed to talk to schedd %s" % schedd)
+        except RuntimeError as e:
+            # schedd not found is common (for example, flocking host with 0 jobs)
+            # we do not need lots of stack traces in the logs for those
+            if "not found" in str(e):
+                logSupport.log.error("Failed to talk to schedd %s - not found" % schedd)
+            else:
+                logSupport.log.exception("Runtime Error. Failed to talk to schedd %s" % schedd)
             continue
         except Exception:
             logSupport.log.exception("Unknown Exception. Failed to talk to schedd %s" % schedd)
__END_PATCH__
popd
