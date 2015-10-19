#!/usr/bin/env python

import unittest
import os, uuid, time
from paths import ROOT_PATH
from src.job import Job, SparkJob, JobCheck

class JobSentinel(object):
    @staticmethod
    def sparkJob():
        uid = str(uuid.uuid4())
        name = "test-job"
        masterurl = "spark://jony-local.local:7077"
        entrypoint = "org.apache.spark.test.Class"
        jar = os.path.join(ROOT_PATH, "test", "resources", "dummy.jar")
        options = {
            "spark.driver.memory": "8g",
            "spark.executor.memory": "8g",
            "spark.shuffle.spill": "true",
            "spark.file.overwrite": "true"
        }
        return SparkJob(uid, name, masterurl, entrypoint, jar, options)

    @staticmethod
    def job():
        uid = str(uuid.uuid4())
        status = "WAITING"
        submittime = long(time.time())
        duration = "MEDIUM"
        sparkjob = JobSentinel.sparkJob()
        return Job(uid, status, submittime, duration, sparkjob)

class JobCheckTestSuite(unittest.TestCase):
    def test_validateMemory(self):
        memory = ["8gb", "8g", "512mb", "512m", "1024M", "16G", "2pb"]
        for entry in memory:
            self.assertEqual(JobCheck.validateMemory(entry), entry.lower())
        memory = ["16gigabytes", "16u", "320b", "gb", "mb"]
        for entry in memory:
            with self.assertRaises(StandardError):
                JobCheck.validateMemory(entry)

    def test_validateEntrypoint(self):
        entries = ["org.apache.spark.Test", "com.wyn.research.Test_core", "Test_core"]
        for entry in entries:
            self.assertEqual(JobCheck.validateEntrypoint(entry), entry)
        entries = ["org-apache", "org.wrong.test.", "another.wrong.Test-test"]
        for entry in entries:
            with self.assertRaises(StandardError):
                JobCheck.validateEntrypoint(entry)

    def test_validateMasterUrl(self):
        master = ["spark://local:7077", "spark://chcs240.co.nz:7079", "spark://192.168.0.1:8080"]
        for entry in master:
            self.assertEqual(JobCheck.validateMasterUrl(entry), entry)
        master = ["http://local:7077", "spark-local:7077"]
        for entry in master:
            with self.assertRaises(StandardError):
                JobCheck.validateMasterUrl(entry)

    def test_validateJarPath(self):
        entries = [os.path.join(ROOT_PATH, "test", "resources", "dummy.jar")]
        for entry in entries:
            self.assertEqual(JobCheck.validateJarPath(entry), entry)
        entries = [os.path.join("local", "dummy.jar"),
            os.path.join(ROOT_PATH, "absolute", "dummy.jar"),
            os.path.join("test", "resources", "dummy.jar")]
        for entry in entries:
            with self.assertRaises(StandardError):
                JobCheck.validateJarPath(entry)

class SparkJobTestSuite(unittest.TestCase):
    def setUp(self):
        self.uid = str(uuid.uuid4())
        self.name = "test-job"
        self.masterurl = "spark://jony-local.local:7077"
        self.entrypoint = "org.apache.spark.test.Class"
        self.jar = os.path.join(ROOT_PATH, "test", "resources", "dummy.jar")
        self.options = {
            "spark.driver.memory": "8g",
            "spark.executor.memory": "8g",
            "spark.shuffle.spill": "true",
            "spark.file.overwrite": "true"
        }

    def tearDown(self):
        pass

    def test_create(self):
        sparkJob = SparkJob(self.uid, self.name, self.masterurl, self.entrypoint, self.jar,
            self.options)
        self.assertEqual(sparkJob.uid, self.uid)
        self.assertEqual(sparkJob.name, self.name)
        self.assertEqual(sparkJob.masterurl, self.masterurl)
        self.assertEqual(sparkJob.entrypoint, self.entrypoint)
        self.assertEqual(sparkJob.jar, self.jar)
        for key, value in self.options.items():
            self.assertEqual(sparkJob.options[key], value)
        # check validator
        with self.assertRaises(StandardError):
            sparkJob = SparkJob(self.uid, self.name, self.masterurl, self.entrypoint, self.jar, {
                "spark.driver.memory": "8",
                "spark.executor.memory": "8"
            })

    def test_convertToDict(self):
        sparkJob = SparkJob(self.uid, self.name, self.masterurl, self.entrypoint, self.jar,
            self.options)
        obj = sparkJob.toDict()
        self.assertEqual(obj["uid"], self.uid)
        self.assertEqual(obj["name"], self.name)
        self.assertEqual(obj["masterurl"], self.masterurl)
        self.assertEqual(obj["entrypoint"], self.entrypoint)
        self.assertEqual(obj["jar"], self.jar)
        self.assertEqual(obj["options"], self.options)
        self.assertEqual(obj["jobconf"], [])

    def test_convertFromDict(self):
        sparkJob = SparkJob(self.uid, self.name, self.masterurl, self.entrypoint, self.jar,
            self.options)
        obj = sparkJob.toDict()
        newSparkJob = SparkJob.fromDict(obj)
        self.assertEqual(newSparkJob.uid, self.uid)
        self.assertEqual(newSparkJob.name, self.name)
        self.assertEqual(newSparkJob.masterurl, self.masterurl)
        self.assertEqual(newSparkJob.entrypoint, self.entrypoint)
        self.assertEqual(newSparkJob.jar, self.jar)
        self.assertEqual(newSparkJob.options, self.options)
        self.assertEqual(obj["jobconf"], [])

    def test_convertFromDictWithJobConf(self):
        jobconf = ["--test.input='/data'", "--test.log=true", "-h", "--quiet"]
        sparkJob = SparkJob(self.uid, self.name, self.masterurl, self.entrypoint, self.jar,
            self.options, jobconf)
        obj = sparkJob.toDict()
        newSparkJob = SparkJob.fromDict(obj)
        self.assertEqual(newSparkJob.uid, self.uid)
        self.assertEqual(newSparkJob.name, self.name)
        self.assertEqual(newSparkJob.masterurl, self.masterurl)
        self.assertEqual(newSparkJob.entrypoint, self.entrypoint)
        self.assertEqual(newSparkJob.jar, self.jar)
        self.assertEqual(newSparkJob.options, self.options)
        self.assertEqual(obj["jobconf"], jobconf)

    def test_execCommand(self):
        sparkJob = SparkJob(self.uid, self.name, self.masterurl, self.entrypoint, self.jar,
            self.options)
        cmd = sparkJob.execCommand()
        self.assertEqual(len(cmd), 16)

    def test_sparkJobWithJobConf(self):
        jobconf = ["--test.input='/data'", "--test.log=true", "-h", "--quiet"]
        sparkJob = SparkJob(self.uid, self.name, self.masterurl, self.entrypoint, self.jar,
            self.options, jobconf)
        self.assertEqual(sparkJob.jobconf, jobconf)

    def test_execCommandWithJobConf(self):
        jobconf = ["--test.input='/data'", "--test.log=true", "-h", "--quiet"]
        sparkJob = SparkJob(self.uid, self.name, self.masterurl, self.entrypoint, self.jar,
            self.options, jobconf)
        cmd = sparkJob.execCommand()
        self.assertEqual(len(cmd), 20)

class JobTestSuite(unittest.TestCase):
    def setUp(self):
        self.uid = str(uuid.uuid4())
        self.status = "WAITING"
        self.submittime = long(time.time())
        self.duration = "MEDIUM"
        self.sparkjob = JobSentinel.sparkJob()

    def tearDown(self):
        pass

    def test_create(self):
        job = Job(self.uid, self.status, self.submittime, self.duration, self.sparkjob)
        self.assertEqual(job.uid, self.uid)
        self.assertEqual(job.status, self.status)
        self.assertEqual(job.submittime, self.submittime)
        self.assertEqual(job.duration, self.duration)
        self.assertEqual(job.sparkjob, self.sparkjob)
        # check passing wrong status and duration
        with self.assertRaises(StandardError):
            Job(self.uid, "WRONG_STATUS", self.submittime, self.duration, self.sparkjob)
        with self.assertRaises(StandardError):
            Job(self.uid, self.status, self.submittime, "WRONG_DURATION", self.sparkjob)

    def test_updateStatus(self):
        job = Job(self.uid, self.status, self.submittime, self.duration, self.sparkjob)
        self.assertEqual(job.status, self.status)
        job.updateStatus("SUBMITTED")
        self.assertEqual(job.status, "SUBMITTED")
        # check update of a wrong status
        with self.assertRaises(StandardError):
            job.updateStatus("WRONG_STATUS")

    def test_convertToDict(self):
        job = Job(self.uid, self.status, self.submittime, self.duration, self.sparkjob)
        obj = job.toDict()
        self.assertEqual(obj["uid"], self.uid)
        self.assertEqual(obj["status"], self.status)
        self.assertEqual(obj["submittime"], self.submittime)
        self.assertEqual(obj["duration"], self.duration)
        self.assertEqual(obj["sparkjob"], self.sparkjob.toDict())

    def test_convertFromDict(self):
        job = Job(self.uid, self.status, self.submittime, self.duration, self.sparkjob)
        obj = job.toDict()
        copy = Job.fromDict(obj)
        self.assertEqual(copy.uid, self.uid)
        self.assertEqual(copy.status, self.status)
        self.assertEqual(copy.submittime, self.submittime)
        self.assertEqual(copy.duration, self.duration)
        self.assertEqual(copy.sparkjob.toDict(), self.sparkjob.toDict())

# Load test suites
def _suites():
    return [
        JobCheckTestSuite,
        SparkJobTestSuite,
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
