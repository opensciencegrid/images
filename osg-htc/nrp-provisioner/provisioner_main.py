#
# prp-osg-pool/provisioner
#
# BSD license, copyright Igor Sfiligoi 2022
#
# Main entry point of the provisioner process
#

import sys
import time
import configparser

import src.provisioner_k8s as provisioner_k8s
import src.provisioner_logging as provisioner_logging
import src.provisioner_htcondor as provisioner_htcondor
import src.event_loop as event_loop
import src.provisioner_backoff as provisioner_backoff

def main(log_fname, namespace, cvmfs_mounts):
   fconfig = configparser.ConfigParser()
   fconfig.read(('pod.conf','osg_provisioner.conf'))
   kconfig = provisioner_k8s.ProvisionerK8SConfig(namespace)
   cconfig = provisioner_htcondor.ProvisionerHTCConfig(namespace)

   # we will distinguish this class by these attrs
   kconfig.additional_labels['osg-provisioner'] = 'wn'
   kconfig.app_name = 'osg-wn'
   cconfig.app_name = 'osg-wn'

   kfconfig = fconfig['k8s'] if ('k8s' in fconfig) else fconfig['DEFAULT']
   kconfig.parse(kfconfig)

   hfconfig = fconfig['htcondor'] if ('htcondor' in fconfig) else fconfig['DEFAULT']
   cconfig.parse(hfconfig)

   kconfig.base_pvc_volumes["cvmfs"] =  "#/cvmfs"
   cvmfsenvs=[]

   # we always need the osg-config and oasis
   for c in (['config-osg','oasis'] + cvmfs_mounts):
      ext='opensciencegrid.org' if c!='stash' else 'osgstorage.org'
      cvmfsenvs.append( "%s.%s"%(c,ext) )

   kconfig.additional_envs['CVMFS_REPOS'] = ",".join(cvmfsenvs)

   log_obj = provisioner_logging.ProvisionerFileLogging(log_fname, want_log_debug=True, also_stdout=True)
   # TBD: Strong security
   schedd_whitelist=hfconfig.get('schedd_whitelist_regexp','.*')
   schedd_obj = provisioner_htcondor.ProvisionerSchedd(log_obj, {schedd_whitelist:'.*'}, cconfig)
   collector_obj = provisioner_htcondor.ProvisionerCollector(log_obj, '.*', cconfig)
   k8s_obj = provisioner_k8s.ProvisionerK8S(kconfig)
   k8s_obj.authenticate()

   max_pods_per_cluster = int(kfconfig.get('max_pods_per_cluster','20'))
   max_submit_pods_per_cluster = int(kfconfig.get('max_submit_pods_per_cluster','1000'))
   # clusters with no claimed pods get only this many, until one is claimed
   trial_pods = int(kfconfig.get('trial_pods','2'))
   sleep_time = int(fconfig['DEFAULT'].get('sleep_time','120'))

   # stop provisioning for a while for clusters whose pods keep exiting unclaimed
   backoff_obj = provisioner_backoff.ProvisionerBackoff(int(kfconfig.get('backoff_unclaimed_exits','2')),
                                                        int(kfconfig.get('backoff_time','3600')),
                                                        int(kfconfig.get('backoff_max_time','28800')))

   el = event_loop.ProvisionerEventLoop(log_obj, schedd_obj, collector_obj, k8s_obj, max_pods_per_cluster, max_submit_pods_per_cluster, backoff_obj, trial_pods)
   while True:
      log_obj.log_debug("[Main] Iteration started, schedd whitelist='%s'"%schedd_whitelist)
      try:
         el.one_iteration()
      except:
         log_obj.log_debug("[Main] Exception in one_iteration")
      log_obj.sync()
      time.sleep(sleep_time)

if __name__ == "__main__":
   # execute only if run as a script
   main(sys.argv[1], sys.argv[2], sys.argv[3].split(","))

