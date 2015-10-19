#!/usr/bin/env python

import unittest
import os
from paths import ROOT_PATH
from types import LongType
from src.job import SparkJob, Job, STATUSES, CAN_CLOSE_STATUSES
from src.jobmanager import JobManager

class JobManagerTestSuite(unittest.TestCase):
    def setUp(self):
        # we do not validate spark master address, as it is part of the JobCheck tests
        self.masterurl = "spark://jony-local.local:7077"
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

    def tearDown(self):
        pass

    def test_create(self):
        jobManager = JobManager(self.masterurl)
        self.assertEqual(jobManager.masterurl, self.masterurl)
        with self.assertRaises(StandardError):
            JobManager("")

    def test_parseOptions(self):
        jobManager = JobManager(self.masterurl)
        options = jobManager.parseOptions(self.optionsString)
        for key in self.options.keys():
            self.assertEqual(options[key], self.options[key])

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
        jobManager = JobManager(self.masterurl)
        self.checkSparkJob(jobManager, self.options)

    def test_createComplexSparkJob(self):
        jobManager = JobManager(self.masterurl)
        self.checkSparkJob(jobManager, self.optionsString)

    def test_createJob(self):
        jobManager = JobManager(self.masterurl)
        sparkJob = jobManager.createSparkJob(self.name, self.entrypoint, self.jar,
            self.driverMemory, self.executorMemory, self.options)
        job = jobManager.createJob(sparkJob)
        self.assertEqual(job.uid.startswith("job_"), True)
        self.assertEqual(job.status, "CREATED")
        self.assertEqual(job.duration, "MEDIUM")
        self.assertEqual(type(job.submittime) is LongType and job.submittime > 0, True)
        self.assertEqual(type(job.sparkjob), SparkJob)

    def test_closeJob(self):
        # test for non-job entries
        jobManager = JobManager(self.masterurl)
        with self.assertRaises(StandardError):
            jobManager.closeJob({})
        with self.assertRaises(StandardError):
            jobManager.closeJob([])
        with self.assertRaises(StandardError):
            jobManager.closeJob("job")
        # test for already closed or submitted jobs
        sparkJob = jobManager.createSparkJob(self.name, self.entrypoint, self.jar,
            self.driverMemory, self.executorMemory, self.options)
        job = jobManager.createJob(sparkJob)
        for x in STATUSES:
            if x not in CAN_CLOSE_STATUSES:
                job.updateStatus(x)
                with self.assertRaises(StandardError):
                    jobManager.closeJob(job)
        # test closing job
        job = jobManager.createJob(sparkJob)
        self.assertEqual(job.status, "CREATED")
        jobManager.closeJob(job)
        self.assertEqual(job.status, "CLOSED")

    def test_parseJobConf(self):
        jobManager = JobManager(self.masterurl)
        # removing quotes is kind of weird
        variations = ["", "ls -lh /data", "-h --ignore=\"some true\"", "\"some true\""]
        res = [[], ["ls", "-lh", "/data"], ["-h", "--ignore=some true"], ["some true"]]
        for index in range(len(variations)):
            jobconf = jobManager.parseJobConf(variations[index])
            self.assertEqual(jobconf, res[index])

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
