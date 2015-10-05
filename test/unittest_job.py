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
        self.entrypoint = "org.apache.spark.test.Class"
        self.masterurl = "spark://jony-local.local:7077"
        self.options = {
            "spark.driver.memory": "8g",
            "spark.executor.memory": "8g",
            "spark.shuffle.spill": "true",
            "spark.file.overwrite": "true"
        }

    def tearDown(self):
        pass

    def test_create(self):
        job = Job(self.uid, self.status, self.starttime, self.name, self.duration, self.entrypoint,
            self.masterurl, self.options)
        self.assertEqual(job.uid, self.uid)
        self.assertEqual(job.status, self.status)
        self.assertEqual(job.starttime, self.starttime)
        self.assertEqual(job.name, self.name)
        self.assertEqual(job.duration, self.duration)
        self.assertEqual(job.entrypoint, self.entrypoint)
        self.assertEqual(job.masterurl, self.masterurl)
        self.assertEqual(job.options, self.options)
        # check passing wrong status and duration
        with self.assertRaises(StandardError):
            Job(self.uid, "WRONG_STATUS", self.starttime, self.name, self.duration, self.entrypoint,
                self.masterurl, self.options)
        with self.assertRaises(StandardError):
            Job(self.uid, self.status, self.starttime, self.name, "WRONG_DURATION", self.entrypoint,
                self.masterurl, self.options)

    def test_validateMemory(self):
        job = Job(self.uid, self.status, self.starttime, self.name, self.duration, self.entrypoint,
            self.masterurl, self.options)
        memory = ["8gb", "8g", "512mb", "512m", "1024M", "16G", "2pb"]
        for entry in memory:
            self.assertEqual(job.validateMemory(entry), entry.lower())
        memory = ["16gigabytes", "16u", "320b", "gb", "mb"]
        for entry in memory:
            with self.assertRaises(StandardError):
                job.validateMemory(entry)

    def test_validateEntrypoint(self):
        job = Job(self.uid, self.status, self.starttime, self.name, self.duration, self.entrypoint,
            self.masterurl, self.options)
        entries = ["org.apache.spark.Test", "com.wyn.research.Test_core", "Test_core"]
        for entry in entries:
            self.assertEqual(job.validateEntrypoint(entry), entry)
        entries = ["org-apache", "org.wrong.test.", "another.wrong.Test-test"]
        for entry in entries:
            with self.assertRaises(StandardError):
                job.validateEntrypoint(entry)

    def test_validateMasterUrl(self):
        job = Job(self.uid, self.status, self.starttime, self.name, self.duration, self.entrypoint,
            self.masterurl, self.options)
        master = ["spark://local:7077", "spark://chcs240.co.nz:7079", "spark://192.168.0.1:8080"]
        for entry in master:
            self.assertEqual(job.validateMasterUrl(entry), entry)
        master = ["http://local:7077", "spark-local:7077"]
        for entry in master:
            with self.assertRaises(StandardError):
                job.validateMasterUrl(entry)

    def test_updateStatus(self):
        job = Job(self.uid, self.status, self.starttime, self.name, self.duration, self.entrypoint,
            self.masterurl, self.options)
        self.assertEqual(job.status, self.status)
        job.updateStatus("SUBMITTED")
        self.assertEqual(job.status, "SUBMITTED")
        # check update of a wrong status
        with self.assertRaises(StandardError):
            job.updateStatus("WRONG_STATUS")

    def test_convertToDict(self):
        job = Job(self.uid, self.status, self.starttime, self.name, self.duration, self.entrypoint,
            self.masterurl, self.options)
        obj = job.toDict()
        self.assertEqual(obj["uid"], job.uid)
        self.assertEqual(obj["status"], job.status)
        self.assertEqual(obj["starttime"], job.starttime)
        self.assertEqual(obj["name"], job.name)
        self.assertEqual(obj["duration"], job.duration)
        self.assertEqual(obj["entrypoint"], job.entrypoint)
        self.assertEqual(obj["masterurl"], job.masterurl)
        self.assertEqual(obj["options"], job.options)

    def test_convertFromDict(self):
        job = Job(self.uid, self.status, self.starttime, self.name, self.duration, self.entrypoint,
            self.masterurl, self.options)
        obj = job.toDict()
        copy = Job.fromDict(obj)
        self.assertEqual(copy.uid, job.uid)
        self.assertEqual(copy.status, job.status)
        self.assertEqual(copy.starttime, job.starttime)
        self.assertEqual(copy.name, job.name)
        self.assertEqual(copy.duration, job.duration)
        self.assertEqual(copy.entrypoint, job.entrypoint)
        self.assertEqual(copy.masterurl, job.masterurl)
        self.assertEqual(copy.options, job.options)

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
