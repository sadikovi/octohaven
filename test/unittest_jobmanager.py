#!/usr/bin/env python

import unittest
import os
from paths import ROOT_PATH
from types import LongType
from src.job import *
from src.sparkmodule import SparkModule
from src.redisconnector import RedisConnectionPool, RedisConnector
from src.storagemanager import StorageManager
from src.jobmanager import JobManager, ALL_JOBS_KEY
from test.unittest_constants import RedisConst

class JobManagerTestSuite(unittest.TestCase):
    def setUp(self):
        # we do not validate spark master address, as it is part of the JobCheck tests
        test_pool = RedisConnectionPool({
            "host": RedisConst.redisHost(),
            "port": RedisConst.redisPort(),
            "db": RedisConst.redisTestDb()
        })
        self.connector = RedisConnector(test_pool)
        self.connector.flushdb()
        self.masterurl = "spark://jony-local.local:7077"
        self.uiurl = "http://localhost:8080"
        self.uiRunUrl = "http://localhost:4040"
        self.name = "test-job"
        self.entrypoint = "org.apache.spark.test.Class"
        self.driverMemory = "20g"
        self.executorMemory = "40g"
        self.jar = os.path.join(ROOT_PATH, "test", "resources", "dummy.jar")
        self.options = {
            "spark.driver.memory": "8g",
            "spark.executor.memory": "8g",
            "spark.shuffle.spill": "true",
            "spark.file.overwrite": "true",
            "spark.executor.extraJavaOptions": "-XX:+PrintGCDetails -XX:+PrintGCTimeStamps",
            "spark.driver.extraJavaOptions": "-Dfile.encoding=UTF-8 -Dsun.jnu.encoding=UTF-8"
        }
        self.optionsString = "--name \"test\" " + "--master local[4] " + \
            "--conf spark.driver.memory=8g " + "--conf spark.executor.memory=8g " + \
            "--conf spark.shuffle.spill=true " + \
            "--conf \"spark.executor.extraJavaOptions=-XX:+PrintGCDetails -XX:+PrintGCTimeStamps\" " + \
            "--conf \"spark.file.overwrite=true\" " + \
            "--conf \"spark.driver.extraJavaOptions=-Dfile.encoding=UTF-8 -Dsun.jnu.encoding=UTF-8\" "
        # create Spark module and storage manager for job manager
        self.sparkModule = SparkModule(self.masterurl, self.uiurl, self.uiRunUrl)
        self.storageManager = StorageManager(self.connector)


    def tearDown(self):
        pass

    def test_create(self):
        jobManager = JobManager(self.sparkModule, self.storageManager)
        self.assertEqual(type(jobManager.storageManager), StorageManager)
        self.assertEqual(type(jobManager.sparkModule), SparkModule)
        with self.assertRaises(StandardError):
            JobManager(None, None)

    def test_parseOptions(self):
        jobManager = JobManager(self.sparkModule, self.storageManager)
        options = jobManager.parseOptions(self.optionsString)
        for key in self.options.keys():
            self.assertEqual(options[key], self.options[key])

    def test_parseJobConf(self):
        jobManager = JobManager(self.sparkModule, self.storageManager)
        # removing quotes is kind of weird
        variations = ["", "ls -lh /data", "-h --ignore=\"some true\"", "\"some true\""]
        res = [[], ["ls", "-lh", "/data"], ["-h", "--ignore=some true"], ["some true"]]
        for index in range(len(variations)):
            jobconf = jobManager.parseJobConf(variations[index])
            self.assertEqual(jobconf, res[index])

    # Spark job check for different options (as dict and as string)
    def checkSparkJob(self, jobManager, options):
        sparkJob = jobManager.createSparkJob(self.name, self.entrypoint, self.jar,
            self.driverMemory, self.executorMemory, options)
        # check
        self.assertEqual(sparkJob.uid.startswith("spark_"), True)
        self.assertEqual(sparkJob.name, self.name)
        self.assertEqual(sparkJob.entrypoint, self.entrypoint)
        self.assertEqual(sparkJob.jar, self.jar)
        # options should be overriden for spark.driver.memory and spark.executor.memory
        for key, value in self.options.items():
            if key == "spark.driver.memory":
                self.assertEqual(sparkJob.options[key], self.driverMemory)
            elif key == "spark.executor.memory":
                self.assertEqual(sparkJob.options[key], self.executorMemory)
            else:
                self.assertEqual(sparkJob.options[key], value)

    def test_createSimpleSparkJob(self):
        jobManager = JobManager(self.sparkModule, self.storageManager)
        self.checkSparkJob(jobManager, self.options)

    def test_createComplexSparkJob(self):
        jobManager = JobManager(self.sparkModule, self.storageManager)
        self.checkSparkJob(jobManager, self.optionsString)

    def test_createJob(self):
        jobManager = JobManager(self.sparkModule, self.storageManager)
        sparkJob = jobManager.createSparkJob(self.name, self.entrypoint, self.jar,
            self.driverMemory, self.executorMemory, self.options)
        job = jobManager.createJob(sparkJob)
        self.assertEqual(job.uid.startswith("job_"), True)
        self.assertEqual(job.status, CREATED)
        self.assertEqual(job.duration, MEDIUM)
        self.assertEqual(type(job.submittime) is LongType and job.submittime > 0, True)
        self.assertEqual(type(job.sparkjob), SparkJob)

    def test_saveJob(self):
        jobManager = JobManager(self.sparkModule, self.storageManager)
        sparkJob = jobManager.createSparkJob(self.name, self.entrypoint, self.jar,
            self.driverMemory, self.executorMemory, self.options)
        job = jobManager.createJob(sparkJob)
        jobManager.saveJob(job)
        self.assertEqual(jobManager.jobForUid(job.uid).toDict(), job.toDict())
        self.assertEqual(len(self.storageManager.jobsForStatus(job.status)), 1)
        self.assertEqual(len(self.storageManager.jobsForStatus(ALL_JOBS_KEY)), 1)
        with self.assertRaises(StandardError):
            jobManager.saveJob({})
        with self.assertRaises(StandardError):
            jobManager.saveJob(None)

    def test_changeStatus(self):
        jobManager = JobManager(self.sparkModule, self.storageManager)
        sparkJob = jobManager.createSparkJob(self.name, self.entrypoint, self.jar,
            self.driverMemory, self.executorMemory, self.options)
        job = jobManager.createJob(sparkJob)
        oldStatus = job.status
        jobManager.saveJob(job)
        jobManager.changeStatus(job, WAITING, lambda x, y: x != y, True)
        self.assertEqual(jobManager.jobForUid(job.uid).toDict(), job.toDict())
        self.assertEqual(len(self.storageManager.jobsForStatus(job.status)), 1)
        self.assertEqual(len(self.storageManager.jobsForStatus(ALL_JOBS_KEY)), 1)
        self.assertEqual(len(self.storageManager.jobsForStatus(oldStatus)), 0)

    def test_closeJob(self):
        jobManager = JobManager(self.sparkModule, self.storageManager)
        sparkJob = jobManager.createSparkJob(self.name, self.entrypoint, self.jar,
            self.driverMemory, self.executorMemory, self.options)
        job = jobManager.createJob(sparkJob)
        jobManager.saveJob(job)
        jobManager.closeJob(job)
        self.assertEqual(jobManager.jobForUid(job.uid).toDict(), job.toDict())
        self.assertEqual(len(self.storageManager.jobsForStatus(job.status)), 1)
        self.assertEqual(len(self.storageManager.jobsForStatus(ALL_JOBS_KEY)), 1)
        # try closing job that is finished
        jobManager.changeStatus(job, FINISHED, lambda x, y: x != y, True)
        with self.assertRaises(StandardError):
            jobManager.closeJob(job)

    def test_listJobsForStatus(self):
        jobManager = JobManager(self.sparkModule, self.storageManager)
        # status from job statuses
        status = WAITING
        jobs = jobManager.listJobsForStatus(status, limit=30, sort=True)
        self.assertEqual(jobs, [])
        # status made lowercase
        status = WAITING.lower()
        jobs = jobManager.listJobsForStatus(status, limit=30, sort=True)
        self.assertEqual(jobs, [])
        # status is invalid
        with self.assertRaises(StandardError):
            status = "INVALID"
            jobManager.listJobsForStatus(status, limit=30, sort=True)

# Load test suites
def _suites():
    return [
        JobManagerTestSuite
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
