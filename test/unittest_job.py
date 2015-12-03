#!/usr/bin/env python

import unittest
import os, uuid, time, random
from paths import ROOT_PATH
from src.job import *
from src.utils import nextJobId, isJobId, nextSparkJobId, isSparkJobId

class JobSentinel(object):
    @staticmethod
    def sparkJob():
        uid = nextSparkJobId()
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
        uid = nextJobId()
        status = WAITING
        createtime = long(time.time())
        submittime = long(time.time())
        duration = MEDIUM
        sparkjob = JobSentinel.sparkJob()
        return Job(uid, status, createtime, submittime, duration, sparkjob)

class JobCheckTestSuite(unittest.TestCase):
    def test_validateStatus(self):
        status = random.choice(STATUSES)
        self.assertEqual(JobCheck.validateStatus(status), status)
        with self.assertRaises(StandardError):
            JobCheck.validateStatus(tatus.lower())
        with self.assertRaises(StandardError):
            JobCheck.validateStatus("INVALID_STATUS")

    def test_validatePriority(self):
        self.assertEqual(JobCheck.validatePriority(100), 100)
        self.assertEqual(JobCheck.validatePriority(1), 1)
        self.assertEqual(JobCheck.validatePriority(0), 0)
        with self.assertRaises(StandardError):
            self.assertEqual(JobCheck.validatePriority(-1), -1)

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

    def test_validateUiUrl(self):
        ui = ["http://localhost:8080", "http://sandbox:38080", "http://192.168.99.100:8080"]
        for entry in ui:
            self.assertEqual(JobCheck.validateUiUrl(entry), entry)
        ui = ["https://localhost:8020", "http://192.168.99.100"]
        for entry in ui:
            with self.assertRaises(StandardError):
                JobCheck.validateUiUrl(entry)

    def test_validateMasterUrl(self):
        master = ["spark://local:7077", "spark://chcs240.co.nz:7079", "spark://192.168.0.1:8080"]
        for entry in master:
            self.assertEqual(JobCheck.validateMasterUrl(entry), entry)
        master = ["http://local:7077", "spark-local:7077"]
        for entry in master:
            with self.assertRaises(StandardError):
                JobCheck.validateMasterUrl(entry)

    def test_validateJarPath(self):
        entries = [os.path.join(ROOT_PATH, "test", "resources", "dummy.jar"),
            os.path.join(ROOT_PATH, "absolute", "dummy.jar")]
        for entry in entries:
            self.assertEqual(JobCheck.validateJarPath(entry), entry)
        entries = [os.path.join("local", "dummy.jar"),
            os.path.join("test", "resources", "dummy.jar")]
        for entry in entries:
            with self.assertRaises(StandardError):
                JobCheck.validateJarPath(entry)

    def test_validateJobId(self):
        with self.assertRaises(StandardError):
            JobCheck.validateJobUid("test")
        with self.assertRaises(StandardError):
            JobCheck.validateJobUid(uuid.uuid4().hex)
        uid = nextJobId()
        self.assertEqual(JobCheck.validateJobUid(uid), uid)

    def test_validateSparkJobId(self):
        with self.assertRaises(StandardError):
            JobCheck.validateSparkJobUid("test")
        with self.assertRaises(StandardError):
            JobCheck.validateSparkJobUid(uuid.uuid4().hex)
        uid = nextSparkJobId()
        self.assertEqual(JobCheck.validateSparkJobUid(uid), uid)

class SparkJobTestSuite(unittest.TestCase):
    def setUp(self):
        self.uid = nextSparkJobId()
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

    def test_uid(self):
        sparkJob = SparkJob(self.uid, self.name, self.masterurl, self.entrypoint, self.jar,
            self.options)
        self.assertEqual(sparkJob.uid, self.uid)
        with self.assertRaises(StandardError):
            SparkJob(uuid.uuid4().hex, self.name, self.masterurl, self.entrypoint, self.jar,
                self.options)

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
        cmd = sparkJob.execCommand({SPARK_UID_KEY: sparkJob.uid})
        self.assertTrue((SPARK_UID_KEY + "=" + sparkJob.uid) in cmd)
        # increased number of parameters passed with spark uid key
        self.assertEqual(len(cmd), 18)

    def test_sparkJobWithJobConf(self):
        jobconf = ["--test.input='/data'", "--test.log=true", "-h", "--quiet"]
        sparkJob = SparkJob(self.uid, self.name, self.masterurl, self.entrypoint, self.jar,
            self.options, jobconf)
        self.assertEqual(sparkJob.jobconf, jobconf)

    def test_execCommandWithJobConf(self):
        jobconf = ["--test.input='/data'", "--test.log=true", "-h", "--quiet"]
        sparkJob = SparkJob(self.uid, self.name, self.masterurl, self.entrypoint, self.jar,
            self.options, jobconf)
        cmd = sparkJob.execCommand({SPARK_UID_KEY: sparkJob.uid})
        self.assertTrue((SPARK_UID_KEY + "=" + sparkJob.uid) in cmd)
        # increased number of parameters passed with spark uid key
        self.assertEqual(len(cmd), 22)

    def test_clone(self):
        sparkjob = JobSentinel.sparkJob()
        copy = sparkjob.clone()
        self.assertTrue(copy.uid != sparkjob.uid)
        # reset different uids, so we can compare the rest
        copyObj = copy.toDict()
        copyObj["uid"] = None
        obj = sparkjob.toDict()
        obj["uid"] = None
        self.assertEqual(copyObj, obj)

class JobTestSuite(unittest.TestCase):
    def setUp(self):
        self.uid = nextJobId()
        self.status = WAITING
        self.createtime = long(time.time())
        self.submittime = long(time.time())
        self.duration = MEDIUM
        self.sparkjob = JobSentinel.sparkJob()

    def tearDown(self):
        pass

    def test_create(self):
        job = Job(self.uid, self.status, self.createtime, self.submittime,
            self.duration, self.sparkjob)
        self.assertEqual(job.uid, self.uid)
        self.assertEqual(job.status, self.status)
        self.assertEqual(job.submittime, self.submittime)
        self.assertEqual(job.duration, self.duration)
        self.assertEqual(job.sparkjob, self.sparkjob)
        # default priority should be resolved into submittime
        self.assertEqual(job.priority, self.submittime)
        # now if you specify priority defferent from DEFAULT_PRIORITY, it will be assigned
        job = Job(self.uid, self.status, self.createtime, self.submittime,
            self.duration, self.sparkjob, priority=99)
        self.assertEqual(job.priority, 99)
        # check passing wrong status and duration
        with self.assertRaises(StandardError):
            Job(self.uid, "WRONG_STATUS", self.createtime, self.submittime,
                self.duration, self.sparkjob)
        with self.assertRaises(StandardError):
            Job(self.uid, self.status, self.createtime, self.submittime,
                "WRONG_DURATION", self.sparkjob)

    def test_uid(self):
        job = Job(self.uid, self.status, self.createtime, self.submittime,
            self.duration, self.sparkjob)
        self.assertEqual(job.uid, self.uid)
        with self.assertRaises(StandardError):
            Job(uuid.uuid4().hex, self.status, self.createtime, self.submittime, self.duration,
                self.sparkjob)

    def test_updateStatus(self):
        job = Job(self.uid, self.status, self.createtime, self.submittime,
            self.duration, self.sparkjob)
        self.assertEqual(job.status, self.status)
        job.updateStatus(FINISHED)
        self.assertEqual(job.status, FINISHED)
        # check update of a wrong status
        with self.assertRaises(StandardError):
            job.updateStatus("WRONG_STATUS")

    def test_convertToDict(self):
        job = Job(self.uid, self.status, self.createtime, self.submittime,
            self.duration, self.sparkjob)
        obj = job.toDict()
        self.assertEqual(obj["uid"], self.uid)
        self.assertEqual(obj["status"], self.status)
        self.assertEqual(obj["createtime"], self.createtime)
        self.assertEqual(obj["submittime"], self.submittime)
        self.assertEqual(obj["duration"], self.duration)
        self.assertEqual(obj["sparkjob"], self.sparkjob.toDict())
        self.assertEqual(obj["priority"], self.submittime)
        self.assertEqual(obj["finishtime"], FINISH_TIME_NONE)
        # change priority of a job
        job.priority = 99
        obj = job.toDict()
        self.assertEqual(obj["priority"], 99)
        # change finish time
        job.finishtime = currentTimeMillis()
        obj = job.toDict()
        self.assertTrue(obj["finishtime"] >= currentTimeMillis() - 1000L)

    def test_convertFromDict(self):
        job = Job(self.uid, self.status, self.createtime, self.submittime,
            self.duration, self.sparkjob, priority=1)
        obj = job.toDict()
        copy = Job.fromDict(obj)
        self.assertEqual(copy.uid, self.uid)
        self.assertEqual(copy.status, self.status)
        self.assertEqual(copy.createtime, self.createtime)
        self.assertEqual(copy.submittime, self.submittime)
        self.assertEqual(copy.duration, self.duration)
        self.assertEqual(copy.sparkjob.toDict(), self.sparkjob.toDict())
        self.assertEqual(copy.priority, job.priority)
        self.assertEqual(copy.finishtime, FINISH_TIME_NONE)
        # finish job check finish time again
        job.updateFinishTime(currentTimeMillis())
        copy = Job.fromDict(job.toDict())
        self.assertTrue(copy.finishtime >= currentTimeMillis() - 1000L)

    def test_updateSparkAppId(self):
        job = Job(self.uid, self.status, self.createtime, self.submittime,
            self.duration, self.sparkjob, 1)
        self.assertEqual(job.sparkAppId, None)
        obj = job.toDict()
        self.assertEqual(obj["sparkappid"], None)
        self.assertEqual(Job.fromDict(obj).sparkAppId, None)
        # update status and check that is updated everywhere
        sparkAppId = "spark_app12345"
        job.updateSparkAppId(sparkAppId)
        self.assertEqual(job.sparkAppId, sparkAppId)
        obj = job.toDict()
        self.assertEqual(obj["sparkappid"], sparkAppId)
        self.assertEqual(Job.fromDict(obj).sparkAppId, sparkAppId)

    def test_updateFinishTime(self):
        job = Job(self.uid, self.status, self.createtime, self.submittime,
            self.duration, self.sparkjob, 1)
        self.assertEqual(job.finishtime, FINISH_TIME_NONE)
        job.updateFinishTime(FINISH_TIME_UNKNOWN)
        self.assertEqual(job.finishtime, FINISH_TIME_UNKNOWN)
        now = currentTimeMillis()
        job.updateFinishTime(now)
        self.assertEqual(job.finishtime, now)
        # check out of range time
        job.updateFinishTime(-1000L)
        self.assertEqual(job.finishtime, FINISH_TIME_UNKNOWN)

    def test_updateStartTime(self):
        job = Job(self.uid, self.status, self.createtime, self.submittime,
            self.duration, self.sparkjob, 1)
        self.assertEqual(job.starttime, self.submittime)
        job.updateStartTime(currentTimeMillis())
        self.assertTrue(job.starttime >= currentTimeMillis() - 1000L)

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
