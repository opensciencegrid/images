#
# Unit tests for the provisioning back-off
#
# Run from the provisioner directory:
#   python3 -m unittest discover -s tests
#

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from src import provisioner_backoff
from src import provisioner_clustering
from src import event_loop

SHAPE = {'PodCPUs': '1', 'PodMemory': '4096', 'PodDisk': '8000000', 'PodGPUs': '0'}
OTHER_SHAPE = {'PodCPUs': '19', 'PodMemory': '4096', 'PodDisk': '8000000', 'PodGPUs': '0'}

def pod(name, phase, shape=SHAPE):
   el = dict(shape)
   el.update({'Name': name, 'Phase': phase, 'StartTime': None, 'HasContainers': True})
   return el

def startd(name, state='Unclaimed', job_starts=None):
   ad = {'Name': 'slot1@%s'%name, 'K8SPodName': name, 'State': state}
   if job_starts!=None:
      ad['JobStarts'] = '%i'%job_starts
   return ad

def clusters(pods, startds):
   return provisioner_clustering.ProvisionerClustering().cluster_k8s_pods(pods, startds)

def cluster_id(shape=SHAPE):
   return list(clusters([pod('x', 'Running', shape)], []).keys())[0]

class TestBackoff(unittest.TestCase):
   def setUp(self):
      self.b = provisioner_backoff.ProvisionerBackoff(max_unclaimed_exits=2, backoff_time=3600, max_backoff_time=8*3600)
      self.cid = cluster_id()

   def run_pod(self, name, now, claimed=False, job_starts=None, end_phase='Succeeded', shape=SHAPE):
      """One pod lifecycle: running with a startd, then gone into end_phase"""
      state = 'Claimed' if claimed else 'Unclaimed'
      self.b.update(clusters([pod(name, 'Running', shape)], [startd(name, state, job_starts)]), now)
      return self.b.update(clusters([pod(name, end_phase, shape)], []), now+60)

   def test_suspends_after_unclaimed_exits(self):
      self.run_pod('p1', 1000)
      self.assertEqual(self.b.suspended_for(self.cid, 1100), 0)
      msgs = self.run_pod('p2', 1100)
      self.assertEqual(len(msgs), 1)
      self.assertEqual(self.b.suspended_for(self.cid, 1160), 3600)
      self.assertEqual(self.b.get_state(self.cid), (2, 1))

   def test_claim_resets(self):
      self.run_pod('p1', 1000)
      self.run_pod('p2', 1100, claimed=True)
      self.run_pod('p3', 1200)
      self.assertEqual(self.b.suspended_for(self.cid, 1300), 0)
      self.assertEqual(self.b.get_state(self.cid), (1, 0))

   def test_job_starts_counts_as_claimed(self):
      # a job may come and go between two polls; JobStarts still shows it
      self.run_pod('p1', 1000, job_starts=1)
      self.run_pod('p2', 1100, job_starts=1)
      self.assertEqual(self.b.suspended_for(self.cid, 1200), 0)

   def test_claim_during_suspension_clears_it(self):
      self.run_pod('p1', 1000)
      self.run_pod('p2', 1100)
      self.assertGreater(self.b.suspended_for(self.cid, 1200), 0)
      msgs = self.b.update(clusters([pod('p3', 'Running')], [startd('p3', 'Claimed')]), 1300)
      self.assertEqual(len(msgs), 1)
      self.assertEqual(self.b.suspended_for(self.cid, 1300), 0)
      self.assertEqual(self.b.get_state(self.cid), (0, 0))

   def test_failed_and_vanished_pods_are_neutral(self):
      self.run_pod('p1', 1000, end_phase='Failed')
      self.b.update(clusters([pod('p2', 'Running')], [startd('p2')]), 1100)
      self.b.update(clusters([], []), 1200)  # p2 vanished
      self.run_pod('p3', 1300)
      self.assertEqual(self.b.suspended_for(self.cid, 1400), 0)
      self.assertEqual(self.b.get_state(self.cid), (1, 0))

   def test_pods_that_never_started_a_startd_are_neutral(self):
      for name in ('p1', 'p2', 'p3'):
         self.b.update(clusters([pod(name, 'Pending')], []), 1000)
         self.b.update(clusters([pod(name, 'Succeeded')], []), 1100)
      self.assertEqual(self.b.suspended_for(self.cid, 1200), 0)

   def test_pods_first_seen_finished_are_ignored(self):
      # e.g. pods from before a provisioner restart
      self.b.update(clusters([pod('old1', 'Succeeded'), pod('old2', 'Succeeded')], []), 1000)
      self.assertEqual(self.b.suspended_for(self.cid, 1000), 0)

   def test_no_extension_during_suspension_then_doubling_and_cap(self):
      self.run_pod('p1', 1000)
      self.run_pod('p2', 1000)
      first = self.b.suspended_for(self.cid, 1060)
      self.run_pod('p3', 2000)  # leftover pod idling out during the suspension
      self.assertEqual(self.b.suspended_for(self.cid, 1060), first)
      t = 1060+first
      durations = []
      for i in range(6):
         self.run_pod('q%i'%i, t)
         d = self.b.suspended_for(self.cid, t+60)
         durations.append(d)
         t += 60+d
      self.assertEqual(durations, [7200, 14400, 28800, 28800, 28800, 28800])

   def test_clusters_are_independent(self):
      other = cluster_id(OTHER_SHAPE)
      self.run_pod('a1', 1000, shape=OTHER_SHAPE)
      self.run_pod('a2', 1100, shape=OTHER_SHAPE)
      self.assertGreater(self.b.suspended_for(other, 1200), 0)
      self.assertEqual(self.b.suspended_for(self.cid, 1200), 0)

   def test_disabled(self):
      b = provisioner_backoff.ProvisionerBackoff(max_unclaimed_exits=0)
      for name in ('p1', 'p2', 'p3'):
         b.update(clusters([pod(name, 'Running')], [startd(name)]), 1000)
         self.assertEqual(b.update(clusters([pod(name, 'Succeeded')], []), 1100), [])
      self.assertEqual(b.suspended_for(self.cid, 1200), 0)


class FakeLog:
   def __init__(self):
      self.lines = []
   def log_debug(self, m): self.lines.append(m)
   def log_info(self, m): self.lines.append(m)
   def log_error(self, m): self.lines.append(m)
   def sync(self): pass

class FakeSchedd:
   def __init__(self, n_idle): self.n_idle = n_idle
   def query_idle(self, projection=[]):
      return [{'JobStatus': 1, 'RequestCPUs': 1, 'RequestMemory': 4096, 'RequestDisk': 8000000} for i in range(self.n_idle)]

class FakeCollector:
   def __init__(self): self.ads = []
   def query(self, projection=[]):
      self.projection = projection
      return self.ads

class FakeK8S:
   def __init__(self):
      self.pods = []
      self.submitted = []
   def query(self): return self.pods
   def submit(self, attrs, n_pods=1):
      self.submitted.append(n_pods)
      return 'job-%i'%len(self.submitted)

class TestEventLoopBackoff(unittest.TestCase):
   def make_loop(self, backoff, trial_pods=0, n_idle=8):
      self.log = FakeLog()
      self.collector = FakeCollector()
      self.k8s = FakeK8S()
      return event_loop.ProvisionerEventLoop(self.log, FakeSchedd(n_idle), self.collector, self.k8s, 20, 1000, backoff, trial_pods)

   def test_suspended_cluster_is_not_provisioned(self):
      b = provisioner_backoff.ProvisionerBackoff(max_unclaimed_exits=2, backoff_time=3600)
      el = self.make_loop(b)
      el.one_iteration()
      self.assertEqual(self.k8s.submitted, [3])  # 1+8/4 pods for 8 idle jobs
      self.assertEqual(self.collector.projection, ['JobStarts'])
      # two of those pods idle out without ever being claimed
      self.k8s.pods = [pod('p1', 'Running'), pod('p2', 'Running')]
      self.collector.ads = [startd('p1'), startd('p2')]
      el.one_iteration()
      self.k8s.pods = [pod('p1', 'Succeeded'), pod('p2', 'Succeeded')]
      self.collector.ads = []
      self.k8s.submitted = []
      el.one_iteration()
      self.assertEqual(self.k8s.submitted, [])
      self.assertTrue(any('suspending provisioning' in l for l in self.log.lines))
      self.assertTrue(any('provisioning suspended for' in l for l in self.log.lines))

   def test_no_backoff_keeps_old_behaviour(self):
      el = self.make_loop(None)
      self.k8s.pods = [pod('p1', 'Succeeded'), pod('p2', 'Succeeded')]
      el.one_iteration()
      self.assertEqual(self.k8s.submitted, [3])

   def test_trial_pods_until_claimed(self):
      el = self.make_loop(None, trial_pods=2, n_idle=40)
      el.one_iteration()
      self.assertEqual(self.k8s.submitted, [2])  # not 1+40/4=11
      # the trial pods wait unclaimed: nothing more
      self.k8s.pods = [pod('p1', 'Running'), pod('p2', 'Running')]
      self.collector.ads = [startd('p1'), startd('p2')]
      self.k8s.submitted = []
      el.one_iteration()
      self.assertEqual(self.k8s.submitted, [])
      # one gets claimed: the cluster gets the full number
      self.collector.ads = [startd('p1', 'Claimed'), startd('p2')]
      el.one_iteration()
      self.assertEqual(self.k8s.submitted, [10])  # 11 wanted, p2 still unclaimed

   def test_trial_pods_below_limit_changes_nothing(self):
      el = self.make_loop(None, trial_pods=2, n_idle=2)
      el.one_iteration()
      self.assertEqual(self.k8s.submitted, [1])

   def test_trial_pods_disabled(self):
      el = self.make_loop(None, trial_pods=0, n_idle=40)
      el.one_iteration()
      self.assertEqual(self.k8s.submitted, [11])

if __name__ == '__main__':
   unittest.main()
