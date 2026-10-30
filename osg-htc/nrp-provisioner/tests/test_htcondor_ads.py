#
# Unit tests for turning HTCondor ads into the provisioner's job/startd dictionaries,
# and for the job clustering built on top of them.
#
# The ads are synthetic (no real users or paths), but use the same attribute names
# and expression forms that real schedds return for the provisioner's projection.
# Needs the htcondor2/classad2 bindings (present in the provisioner image).
#
# Run from the provisioner directory:
#   python3 -m unittest discover -s tests
#

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

try:
   import classad2
   from src import provisioner_htcondor
   from src import provisioner_clustering
except ImportError:
   classad2 = None

JOBS = """
[ ClusterId = 1; ProcId = 0; JobStatus = 1; RequestCPUs = 1;
  RequestMemory = ifThenElse(MemoryUsage isnt undefined,MemoryUsage,500);
  RequestDisk = 8000001 ]
[ ClusterId = 2; ProcId = 0; JobStatus = 1; RequestCPUs = 2;
  RequestMemory = 5000; RequestDisk = 20971520; RequestGPUs = 1 ]
[ ClusterId = 3; ProcId = 0; JobStatus = 1; RequestCPUs = 2;
  RequestMemory = 4096; RequestDisk = 8000000 ]
[ ClusterId = 4; ProcId = 0; JobStatus = 1; RequestCPUs = 2;
  RequestMemory = 4100; DiskUsage = 9000000; RequestDisk = DiskUsage; RequestGPUs = 1 ]
"""

STARTDS = """
[ Name = "slot1@pod-a"; AuthenticatedIdentity = "pool@cm.example"; State = "Claimed";
  Activity = "Busy"; K8SPodName = "pod-a"; JobStarts = 2; HAS_SINGULARITY = false ]
[ Name = "slot1@pod-b"; AuthenticatedIdentity = "pool@cm.example"; State = "Unclaimed";
  Activity = "Idle"; K8SPodName = "pod-b" ]
[ Name = "slot1@pod-c"; AuthenticatedIdentity = "someone@elsewhere"; State = "Unclaimed";
  K8SPodName = "pod-c" ]
[ Name = "slot1@pod-d"; State = "Unclaimed"; K8SPodName = "pod-d" ]
"""

class Log:
   def __init__(self): self.lines = []
   def log_debug(self, m): self.lines.append(m)
   log_info = log_error = log_debug
   def sync(self): pass

@unittest.skipIf(classad2 is None, "htcondor2/classad2 bindings not installed")
class TestJobConversion(unittest.TestCase):
   def convert(self):
      config = provisioner_htcondor.ProvisionerHTCConfig("ns")
      schedd = provisioner_htcondor.ProvisionerSchedd(Log(), {".*": ".*"}, config)
      jobs = []
      schedd._append_jobs("schedd.example", jobs, list(classad2.parseAds(JOBS)))
      return {j['ClusterId']: j for j in jobs}

   def test_values_become_strings_and_schedd_is_recorded(self):
      j = self.convert()['2']
      self.assertEqual(j['ScheddName'], "schedd.example")
      self.assertEqual(j['RequestCPUs'], "2")
      self.assertEqual(j['JobStatus'], "1")
      self.assertEqual(j['RequestGPUs'], "1")

   def test_memory_rounds_up_to_1gb_and_small_values_are_dropped(self):
      jobs = self.convert()
      self.assertNotIn('RequestMemory', jobs['1'])      # expression evaluates to 500 < 4096: treated as unset
      self.assertEqual(jobs['2']['RequestMemory'], "5120")
      self.assertEqual(jobs['3']['RequestMemory'], "4096")  # exact multiple stays
      self.assertEqual(jobs['4']['RequestMemory'], "5120")

   def test_disk_rounds_up_to_4gb_and_expressions_are_evaluated(self):
      jobs = self.convert()
      self.assertEqual(jobs['1']['RequestDisk'], "12000000")
      self.assertEqual(jobs['2']['RequestDisk'], "24000000")
      self.assertEqual(jobs['3']['RequestDisk'], "8000000")
      self.assertEqual(jobs['4']['RequestDisk'], "12000000")  # RequestDisk = DiskUsage = 9000000

   def test_clustering_by_shape_with_defaults(self):
      jobs = list(self.convert().values())
      groups = provisioner_clustering.ProvisionerClustering().cluster_schedd_jobs(jobs)
      counts = {k: g.count_idle() for k, g in groups.items()}
      self.assertEqual(counts, {
         "1;4096;12000000;;0;;": 1,   # memory unset -> default 4096, GPUs unset -> 0
         "2;5120;24000000;;1;;": 1,
         "2;4096;8000000;;0;;": 1,
         "2;5120;12000000;;1;;": 1,
      })
      attrs = groups["2;5120;24000000;;1;;"].get_attr_dict()
      self.assertEqual(attrs['CPUs'], "2")
      self.assertEqual(attrs['GPUs'], "1")

@unittest.skipIf(classad2 is None, "htcondor2/classad2 bindings not installed")
class TestCollectorConversion(unittest.TestCase):
   def setUp(self):
      self.ads = list(classad2.parseAds(STARTDS))
      self.queries = []
      outer = self
      class FakeCollector:
         def query(self, **kwargs):
            outer.queries.append(kwargs)
            return outer.ads
      self.orig = provisioner_htcondor.htcondor2.Collector
      provisioner_htcondor.htcondor2.Collector = lambda *a, **k: FakeCollector()

   def tearDown(self):
      provisioner_htcondor.htcondor2.Collector = self.orig

   def test_startd_ads(self):
      config = provisioner_htcondor.ProvisionerHTCConfig("osg-test")
      config.app_name = "osg-direct"; config.k8s_domain = "example.org"
      coll = provisioner_htcondor.ProvisionerCollector(Log(), "pool@cm\\.example", config)
      startds = {s['K8SPodName']: s for s in coll.query(projection=['JobStarts'])}
      # only ads with a trusted identity survive; ads without one are ignored
      self.assertEqual(sorted(startds), ["pod-a", "pod-b"])
      self.assertEqual(startds['pod-a']['State'], "Claimed")
      self.assertEqual(startds['pod-a']['JobStarts'], "2")
      self.assertEqual(startds['pod-a']['HAS_SINGULARITY'], "False")
      self.assertNotIn('JobStarts', startds['pod-b'])
      q = self.queries[0]
      self.assertIn('JobStarts', q['projection'])
      self.assertIn('K8SNamespace=?="osg-test"', q['constraint'])
      self.assertIn('K8SProvisionerName=?="osg-direct"', q['constraint'])

if __name__ == '__main__':
   unittest.main()
