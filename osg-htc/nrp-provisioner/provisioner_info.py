#!/bin/env python3
#
# prp-osg-pool/provisioner
#
# BSD license, copyright Igor Sfiligoi 2022
#
# Main entry point of the provisioner process
#

import sys,os
import time
import configparser

import src.provisioner_k8s as provisioner_k8s
import src.provisioner_logging as provisioner_logging
import src.provisioner_htcondor as provisioner_htcondor
import src.event_loop as event_loop

def main(namespace):
   fconfig = configparser.ConfigParser()
   fconfig.read(('pod.conf','osg_provisioner.conf'))
   kconfig = provisioner_k8s.ProvisionerK8SConfig(namespace)
   cconfig = provisioner_htcondor.ProvisionerHTCConfig(namespace)

   # we will distinguish this class by these attrs
   kconfig.additional_labels['osg-provisioner'] = 'wn'
   kconfig.app_name = 'osg-wn'
   cconfig.app_name = 'osg-wn'

   if 'k8s' in fconfig:
      kconfig.parse(fconfig['k8s'])
   else:
      kconfig.parse(fconfig['DEFAULT'])

   hfconfig = fconfig['htcondor'] if ('htcondor' in fconfig) else fconfig['DEFAULT']
   cconfig.parse(hfconfig)

   log_obj = provisioner_logging.ProvisionerStdoutLogging(want_log_debug=True)
   # TBD: Strong security
   schedd_whitelist=hfconfig.get('schedd_whitelist_regexp','.*')
   schedd_obj = provisioner_htcondor.ProvisionerSchedd(log_obj, {schedd_whitelist:'.*'}, cconfig)
   collector_obj = provisioner_htcondor.ProvisionerCollector(log_obj, '.*', cconfig)
   k8s_obj = provisioner_k8s.ProvisionerK8S(kconfig)
   k8s_obj.authenticate()

   el = event_loop.ProvisionerEventLoop(log_obj, schedd_obj, collector_obj, k8s_obj, 1, 10000)
   (schedd_clusters, k8s_clusters) = el.query_system()
   all_clusters_set = set(schedd_clusters.keys())|set(k8s_clusters.keys())
   print("%-39s %9s %9s %9s %9s %9s %9s"%("Cluster (CPUs;MEM;DISK;;GPUs;;)","Idle Jobs","Wait Pods","Unmatched","Run Pods","Failed P","Unknown P"))
   print("="*(39+1+9+1+9+1+9+1+9+1+9+1+9))
   ckeys=list(all_clusters_set)
   ckeys.sort()
   for ckey in ckeys:
     sched_cnt=schedd_clusters[ckey].count_idle() if (ckey in schedd_clusters) else 0
     (waiting_cnt,unmatched_cnt,claimed_cnt,failed_cnt,unknown_cnt) = k8s_clusters[ckey].count_states() if (ckey in k8s_clusters) else (0,0,0,0,0)
     if (sched_cnt+waiting_cnt+unmatched_cnt+claimed_cnt+failed_cnt+unknown_cnt)>0:
       # do not report all zeros
       print("%-39s %9i %9i %9i %9i %9i %9i"%(ckey, sched_cnt,waiting_cnt,unmatched_cnt,claimed_cnt,failed_cnt,unknown_cnt))

if __name__ == "__main__":
   # execute only if run as a script
   main(sys.argv[1] if len(sys.argv)>1 else os.environ['K8S_NAMESPACE'])

