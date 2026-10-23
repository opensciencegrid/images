#
# Unit tests for ProvisionerSchedd: the schedd list, the job query constraint and
# failure handling. The collector and schedds are faked; no network.
# Needs the htcondor2/classad2 bindings (present in the provisioner image).
#
# Run from the provisioner directory:
#   python3 -m unittest discover -s tests
#

import configparser
import glob
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

try:
   import classad2
   from src import provisioner_htcondor
except ImportError:
   classad2 = None

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
# the sample config, plus every namespace config when run inside the nrp-provisioner repo (k8s/)
CONFIGS = {'sample': os.path.join(TESTS_DIR, 'sample_osg_provisioner.conf')}
CONFIGS.update((os.path.basename(os.path.dirname(p)), p)
               for p in sorted(glob.glob(os.path.join(TESTS_DIR, '..', '..', 'k8s', 'osg-*', 'osg_provisioner.conf'))))

SCHEDDS = """
[ Name = "ap1.example.org"; AuthenticatedIdentity = "ap1@pool"; MyAddress = "<192.0.2.1:9618>";
  CondorVersion = "$CondorVersion: 25.0.0 $"; CondorPlatform = "$CondorPlatform: X86_64 $" ]
[ Name = "ap2.example.org"; AuthenticatedIdentity = "ap2@pool"; MyAddress = "<192.0.2.2:9618>";
  CondorVersion = "$CondorVersion: 25.0.0 $"; CondorPlatform = "$CondorPlatform: X86_64 $" ]
[ Name = "other.example.com"; AuthenticatedIdentity = "x@pool"; MyAddress = "<192.0.2.3:9618>" ]
[ Name = "noidentity.example.org"; MyAddress = "<192.0.2.4:9618>" ]
"""

JOB = "[ ClusterId = 7; ProcId = 0; JobStatus = 1; RequestCPUs = 1 ]"

class Log:
   def __init__(self): self.lines = []
   def log_debug(self, m): self.lines.append(m)
   log_info = log_error = log_debug

@unittest.skipIf(classad2 is None, "htcondor2/classad2 bindings not installed")
class TestScheddQuery(unittest.TestCase):
   def setUp(self):
      self.collector_queries = []
      self.schedd_queries = []
      self.failing = set()
      outer = self
      class FakeCollector:
         def query(self, **kwargs):
            outer.collector_queries.append(kwargs)
            return list(classad2.parseAds(SCHEDDS))
      class FakeSchedd:
         def __init__(self, location_ad):
            self.name = location_ad['Name']
         def query(self, constraint, projection):
            outer.schedd_queries.append((self.name, constraint, projection))
            if self.name in outer.failing:
               raise RuntimeError("Failed to fetch ads from schedd")
            return list(classad2.parseAds(JOB))
      self.orig = (provisioner_htcondor.htcondor2.Collector, provisioner_htcondor.htcondor2.Schedd)
      provisioner_htcondor.htcondor2.Collector = lambda *a, **k: FakeCollector()
      provisioner_htcondor.htcondor2.Schedd = FakeSchedd

   def tearDown(self):
      provisioner_htcondor.htcondor2.Collector, provisioner_htcondor.htcondor2.Schedd = self.orig

   def schedd(self, whitelist=r".*\.example\.org", **settings):
      config = provisioner_htcondor.ProvisionerHTCConfig("osg-test")
      config.parse(dict(settings))
      log = Log()
      return provisioner_htcondor.ProvisionerSchedd(log, {whitelist: ".*"}, config), log

   def constraint(self):
      return self.schedd_queries[-1][1]

   def test_location_projection_has_what_htcondor2_needs(self):
      s, _ = self.schedd()
      s.query_idle()
      proj = self.collector_queries[0]['projection']
      for attr in ('Name', 'AuthenticatedIdentity', 'MyAddress', 'AddressV1', 'CondorVersion', 'CondorPlatform', 'Machine'):
         self.assertIn(attr, proj)

   def test_whitelist_and_identity_filtering(self):
      s, _ = self.schedd()
      jobs = s.query_idle()
      self.assertEqual(sorted(q[0] for q in self.schedd_queries), ["ap1.example.org", "ap2.example.org"])
      self.assertEqual(sorted(j['ScheddName'] for j in jobs), ["ap1.example.org", "ap2.example.org"])

   def test_apptainer_toggle(self):
      s, _ = self.schedd(apptainer="no")
      s.query_idle()
      self.assertTrue(self.constraint().endswith(" && isUndefined(SingularityImage)"))
      s, _ = self.schedd(apptainer="yes")
      s.query_idle()
      self.assertTrue(self.constraint().endswith(" && (!isUndefined(SingularityImage))"))
      s, _ = self.schedd()  # default is yes
      s.query_idle()
      self.assertTrue(self.constraint().endswith(" && (!isUndefined(SingularityImage))"))

   def test_namespace_matching_and_additional_requirements(self):
      s, _ = self.schedd(additional_requirements="RequestGPUs=?=1")
      s.query_idle(projection=['RequestCPUs'])
      self.assertIn('regexp(RequestK8SNamespace,"osg-test")', self.constraint())
      self.assertIn('(RequestGPUs=?=1)', self.constraint())
      self.assertIn('RequestCPUs', self.schedd_queries[-1][2])
      s, _ = self.schedd(force_k8s_namespace_matching="no")
      s.query_idle()
      self.assertNotIn('RequestK8SNamespace', self.constraint())

   def test_one_failing_schedd_is_logged_and_skipped(self):
      self.failing = {"ap2.example.org"}
      s, log = self.schedd()
      jobs = s.query_idle()
      self.assertEqual([j['ScheddName'] for j in jobs], ["ap1.example.org"])
      self.assertIn("Failed to query HTCondor schedd 'ap2.example.org'", "\n".join(log.lines))

   def test_all_schedds_failing_raises(self):
      self.failing = {"ap1.example.org", "ap2.example.org"}
      s, _ = self.schedd()
      with self.assertRaises(Exception):
         s.query_idle()

   def test_configs_have_exactly_one_container_condition(self):
      for name, path in CONFIGS.items():
         f = configparser.ConfigParser()
         f.read(path)
         h = f['htcondor'] if 'htcondor' in f else f['DEFAULT']
         with self.subTest(config=name):
            config = provisioner_htcondor.ProvisionerHTCConfig(name)
            config.parse(h)
            s = provisioner_htcondor.ProvisionerSchedd(Log(), {".*": ".*"}, config)
            s.query_idle()
            self.assertEqual(self.constraint().count("SingularityImage"), 1)

if __name__ == '__main__':
   unittest.main()
