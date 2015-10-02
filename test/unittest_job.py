#!/usr/bin/env python

import unittest
import uuid
import time
from src.job import Job

class JobTestSuite(unittest.TestCase):
    def setUp(self):
        self.uid = str(uuid.uuid4())
        self.status = "WAITING"
        self.starttime = long(time.time())
        self.name = "test-job"
        self.duration = "MEDIUM"
        self.command = "spark-submit test command"

    def tearDown(self):
        pass

    def test_create(self):
        job = Job(self.uid, self.status, self.starttime, self.name, self.duration, self.command)
        self.assertEqual(job.uid, self.uid)
        self.assertEqual(job.status, self.status)
        self.assertEqual(job.starttime, self.starttime)
        self.assertEqual(job.name, self.name)
        self.assertEqual(job.duration, self.duration)
        self.assertEqual(job.command, self.command)
        # check passing wrong status and duration
        with self.assertRaises(StandardError):
            Job(self.uid, "WRONG_STATUS", self.starttime, self.name, self.duration, self.command)
        with self.assertRaises(StandardError):
            Job(self.uid, self.status, self.starttime, self.name, "WRONG_DURATION", self.command)

    def test_updateStatus(self):
        job = Job(self.uid, self.status, self.starttime, self.name, self.duration, self.command)
        self.assertEqual(job.status, self.status)
        job.updateStatus("SUBMITTED")
        self.assertEqual(job.status, "SUBMITTED")
        # check update of a wrong status
        with self.assertRaises(StandardError):
            job.updateStatus("WRONG_STATUS")

    def test_convertToDict(self):
        job = Job(self.uid, self.status, self.starttime, self.name, self.duration, self.command)
        obj = job.toDict()
        self.assertEqual(obj["uid"], job.uid)
        self.assertEqual(obj["status"], job.status)
        self.assertEqual(obj["starttime"], job.starttime)
        self.assertEqual(obj["name"], job.name)
        self.assertEqual(obj["duration"], job.duration)
        self.assertEqual(obj["command"], job.command)

    def test_convertFromDict(self):
        job = Job(self.uid, self.status, self.starttime, self.name, self.duration, self.command)
        obj = job.toDict()
        copy = Job.fromDict(obj)
        self.assertEqual(copy.uid, job.uid)
        self.assertEqual(copy.status, job.status)
        self.assertEqual(copy.starttime, job.starttime)
        self.assertEqual(copy.name, job.name)
        self.assertEqual(copy.duration, job.duration)
        self.assertEqual(copy.command, job.command)

# Load test suites
def _suites():
    return [
        JobTestSuite
    ]

# Load tests
def loadSuites():
    # global test suite for this module
    gsuite = unittest.TestSuite()
    for suite in _suites():
        gsuite.addTest(unittest.TestLoader().loadTestsFromTestCase(suite))
    return gsuite

if __name__ == '__main__':
    suite = loadSuites()
    print ""
    print "### Running tests ###"
    print "-" * 70
    unittest.TextTestRunner(verbosity=2).run(suite)
