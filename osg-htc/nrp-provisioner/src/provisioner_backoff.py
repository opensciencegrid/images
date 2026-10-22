#
# nrp-provisioner
#
# BSD license
#
# Stop provisioning for clusters whose pods keep exiting without ever being claimed
#
# A pod that reaches the Succeeded phase without its startd ever being claimed
# most likely idled out because the jobs it was provisioned for cannot match it
# (e.g. pinned to another site, or targeting an annex).
# Failed or vanished pods are ignored, since preemption and node problems
# say nothing about the jobs.
#

import time

class ProvisionerBackoff:
   def __init__(self, max_unclaimed_exits=2, backoff_time=3600, max_backoff_time=8*3600):
      """
      Arguments:
         max_unclaimed_exits: int
             Suspend a cluster after this many unclaimed exits without a claim in between (0 disables)
         backoff_time: int
             Length of the first suspension, in seconds; doubled on each repeat
         max_backoff_time: int
             Upper limit for the suspension length, in seconds
      """
      self.max_unclaimed_exits = max_unclaimed_exits
      self.backoff_time = backoff_time
      self.max_backoff_time = max_backoff_time
      self.pods = {}      # pod name -> {'cluster','started','claimed'}
      self.clusters = {}  # cluster id -> {'exits','level','until'}

   def update(self, k8s_clusters, now=None):
      """Process the latest pod states; returns a list of messages worth logging"""
      msgs = []
      if self.max_unclaimed_exits<1:
         return msgs
      if now==None:
         now = time.time()

      seen = set()
      for cluster_id in k8s_clusters.keys():
         for (pod_el, startd_el) in k8s_clusters[cluster_id].elements:
            name = pod_el['Name']
            phase = "%s"%pod_el['Phase']
            seen.add(name)
            rec = self.pods.get(name)
            if phase in ("Pending","Running"):
               if rec==None:
                  rec = {'cluster': cluster_id, 'started': False, 'claimed': False}
                  self.pods[name] = rec
               if startd_el!=None:
                  rec['started'] = True
                  if self._is_claimed(startd_el):
                     rec['claimed'] = True
                     msgs += self._reset(cluster_id)
            elif phase=="Succeeded":
               if rec!=None:
                  if rec['started'] and not rec['claimed']:
                     msgs += self._unclaimed_exit(rec['cluster'], now)
                  del self.pods[name]
            elif rec!=None:
               # Failed or unknown, not the fault of the jobs
               del self.pods[name]

      for name in list(self.pods.keys()):
         if name not in seen:
            # vanished without us seeing the end, ignore
            del self.pods[name]
      return msgs

   def suspended_for(self, cluster_id, now=None):
      """Return the number of seconds the cluster is still suspended for (0 if not suspended)"""
      if self.max_unclaimed_exits<1:
         return 0
      if now==None:
         now = time.time()
      el = self.clusters.get(cluster_id)
      if (el==None) or (el['until']<=now):
         return 0
      return int(el['until']-now)

   def get_state(self, cluster_id):
      """Return (unclaimed exits since the last claim, number of suspensions so far)"""
      el = self.clusters.get(cluster_id)
      if el==None:
         return (0,0)
      return (el['exits'],el['level'])

   # INTERNAL
   def _is_claimed(self, startd_el):
      if "%s"%startd_el.get('State')=="Claimed":
         return True
      try:
         return int("%s"%startd_el.get('JobStarts'))>0
      except ValueError:
         return False

   def _reset(self, cluster_id):
      el = self.clusters.get(cluster_id)
      if el==None:
         return []
      del self.clusters[cluster_id]
      if el['level']>0:
         return ["Cluster '%s' had a pod claimed, provisioning back-off cleared"%cluster_id]
      return []

   def _unclaimed_exit(self, cluster_id, now):
      el = self.clusters.setdefault(cluster_id, {'exits': 0, 'level': 0, 'until': 0})
      el['exits'] += 1
      if (el['exits']>=self.max_unclaimed_exits) and (el['until']<=now):
         # once over the limit, each further unclaimed exit outside a suspension starts a longer one
         duration = min(self.backoff_time*(2**el['level']), self.max_backoff_time)
         el['until'] = now+duration
         el['level'] += 1
         return ["Cluster '%s' had %i pods exit unclaimed, suspending provisioning for %i seconds"%(cluster_id, el['exits'], duration)]
      return []
