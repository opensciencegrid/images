#
# Unit tests for the provisioner file logging
#
# Run from the provisioner directory:
#   python3 -m unittest discover -s tests
#

import io
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from src import provisioner_logging

class TestFileLogging(unittest.TestCase):
   def setUp(self):
      self.dir = tempfile.TemporaryDirectory()
      self.fname = os.path.join(self.dir.name, 'provisioner.log')
      self.stdout = sys.stdout
      sys.stdout = io.StringIO()

   def tearDown(self):
      sys.stdout = self.stdout
      self.dir.cleanup()

   def read_file(self):
      with open(self.fname) as fd:
         return fd.read()

   def test_also_stdout_mirrors_the_file(self):
      log = provisioner_logging.ProvisionerFileLogging(self.fname, dated=False, want_log_debug=True, also_stdout=True)
      log.log_debug("first")
      log.log_error("second")
      self.assertEqual(sys.stdout.getvalue(), "")  # nothing until sync
      log.sync()
      self.assertEqual(sys.stdout.getvalue(), self.read_file())
      self.assertIn("[DEBUG] first", self.read_file())
      self.assertIn("[ERROR] second", self.read_file())
      log.log_info("third")
      log.sync()
      self.assertEqual(sys.stdout.getvalue(), self.read_file())
      self.assertEqual(self.read_file().count("\n"), 3)

   def test_default_is_file_only(self):
      log = provisioner_logging.ProvisionerFileLogging(self.fname, dated=False, want_log_debug=True)
      log.log_info("only in the file")
      log.sync()
      self.assertEqual(sys.stdout.getvalue(), "")
      self.assertIn("[INFO] only in the file", self.read_file())

   def test_debug_filtering_applies_to_both(self):
      log = provisioner_logging.ProvisionerFileLogging(self.fname, dated=False, want_log_debug=False, also_stdout=True)
      log.log_debug("hidden")
      log.log_info("shown")
      log.sync()
      self.assertNotIn("hidden", sys.stdout.getvalue())
      self.assertNotIn("hidden", self.read_file())
      self.assertIn("shown", sys.stdout.getvalue())

if __name__ == '__main__':
   unittest.main()
