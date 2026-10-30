#
# Unit tests for grouping jobs and pods by shape, with plain dictionaries
# (no HTCondor bindings needed).
#
# Run from the provisioner directory:
#   python3 -m unittest discover -s tests
#

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from src import provisioner_clustering

def job(**extra):
   j = {'JobStatus': '1', 'RequestCPUs': '1', 'RequestMemory': '4096', 'RequestDisk': '8000000', 'RequestGPUs': '1'}
   j.update(extra)
   return j

# what ProvisionerK8S.submit labels a pod with, for the job shape above
POD = {'Name': 'p1', 'Phase': 'Running', 'StartTime': None, 'HasContainers': True,
       'PodCPUs': '1', 'PodMemory': '4096', 'PodDisk': '8000000', 'PodGPUs': '1'}

class TestUnsupportedAttributes(unittest.TestCase):
   def setUp(self):
      self.c = provisioner_clustering.ProvisionerClustering()

   def test_jobs_requesting_unsupported_attributes_group_with_their_pods(self):
      jobs = [job(), job(RequestGPUTypes='NVIDIA-A10'), job(RequestLabels='a:b'), job(RequestDiskVolumes='pvc:/data')]
      job_groups = self.c.cluster_schedd_jobs(jobs)
      pod_groups = self.c.cluster_k8s_pods([POD], [])
      self.assertEqual(list(job_groups.keys()), list(pod_groups.keys()))
      self.assertEqual(job_groups[list(job_groups)[0]].count_idle(), 4)

   def test_supported_attributes_still_split_groups(self):
      job_groups = self.c.cluster_schedd_jobs([job(), job(RequestGPUs='2'), job(RequestCPUs='4')])
      self.assertEqual(len(job_groups), 3)

if __name__ == '__main__':
   unittest.main()
