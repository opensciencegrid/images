#
# Unit tests for the k8s Job submission
#
# The kubernetes client (>= 34) validates request bodies before sending them,
# so run submit() through the real client and only intercept the network send.
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
   import kubernetes
   from src import provisioner_k8s
except ImportError:
   kubernetes = None

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
# the sample config, plus every namespace config when run inside the nrp-provisioner repo (k8s/)
CONFIGS = {'sample': os.path.join(TESTS_DIR, 'sample_osg_provisioner.conf')}
CONFIGS.update((os.path.basename(os.path.dirname(p)), p)
               for p in sorted(glob.glob(os.path.join(TESTS_DIR, '..', '..', 'k8s', 'osg-*', 'osg_provisioner.conf'))))

class Sent(Exception):
   pass

@unittest.skipIf(kubernetes is None, "kubernetes client not installed")
class TestSubmit(unittest.TestCase):
   def setUp(self):
      self.sent = []
      self.orig_call_api = kubernetes.client.ApiClient.call_api
      def fake_call_api(api_client, method, url, header_params=None, body=None, *args, **kwargs):
         self.sent.append(body)
         raise Sent()
      kubernetes.client.ApiClient.call_api = fake_call_api

   def tearDown(self):
      kubernetes.client.ApiClient.call_api = self.orig_call_api

   def make_k8s(self, name, use_large_limit):
      f = configparser.ConfigParser()
      f.read(CONFIGS[name])
      k = provisioner_k8s.ProvisionerK8SConfig(name if name.startswith('osg-') else 'osg-test')
      k.parse(f['k8s'] if 'k8s' in f else f['DEFAULT'])
      k.base_pvc_volumes['cvmfs'] = "#/cvmfs"
      k.use_large_limit = use_large_limit
      return provisioner_k8s.ProvisionerK8S(k)

   def submit(self, k8s, cpus, gpus):
      with self.assertRaises(Sent):  # Sent means the body passed the client validation
         k8s.submit({'CPUs': cpus, 'GPUs': gpus, 'Memory': "8192", 'Disk': "8000000"}, 2)
      return self.sent[-1]

   def test_all_configs_pass_client_validation(self):
      for name in CONFIGS:
         for large in ('yes', 'no'):
            for gpus in ('0', '1'):
               with self.subTest(config=name, use_large_limit=large, gpus=gpus):
                  self.submit(self.make_k8s(name, large), "3", gpus)

   def test_quantities_are_strings(self):
      body = self.submit(self.make_k8s('sample', 'yes'), "3", "1")
      res = body['spec']['template']['spec']['containers'][0]['resources']
      self.assertEqual(res['requests']['cpu'], "2.25")
      self.assertEqual(res['limits']['cpu'], "3.25")
      self.assertEqual(res['requests']['nvidia.com/gpu'], "1")
      body = self.submit(self.make_k8s('sample', 'no'), "3", "0")
      res = body['spec']['template']['spec']['containers'][0]['resources']
      self.assertEqual(res['requests']['cpu'], "3")
      self.assertNotIn('nvidia.com/gpu', res['requests'])

   def test_preemption_does_not_fail_the_job(self):
      body = self.submit(self.make_k8s('sample', 'no'), "1", "0")
      self.assertEqual(body['spec']['backoffLimit'], 0)
      self.assertEqual(body['spec']['template']['spec']['restartPolicy'], 'Never')  # required by podFailurePolicy
      self.assertEqual(body['spec']['podFailurePolicy']['rules'],
                       [{'action': 'Ignore', 'onPodConditions': [{'type': 'DisruptionTarget'}]}])

if __name__ == '__main__':
   unittest.main()
