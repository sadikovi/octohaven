#!/usr/bin/env python

import unittest, os, json, src.octo.utils as utils
from paths import ROOT_PATH
from src.octo.sparkjob import SparkJob
from src.octo.sparkmodule import SPARK_OCTOHAVEN_JOB_ID

class SparkJobTestSuite(unittest.TestCase):
    def setUp(self):
        self.uid = 1234567
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
        sparkJob = SparkJob(self.uid, self.name, self.entrypoint, self.jar, self.options)
        self.assertEqual(sparkJob.uid, self.uid)
        self.assertEqual(sparkJob.name, self.name)
        self.assertEqual(sparkJob.entrypoint, self.entrypoint)
        self.assertEqual(sparkJob.jar, self.jar)
        for key, value in self.options.items():
            self.assertEqual(sparkJob.options[key], value)
        self.assertEqual(sparkJob.jobconf, [])
        # check validator
        with self.assertRaises(StandardError):
            sparkJob = SparkJob(self.uid, self.name, self.entrypoint, self.jar, {
                "spark.driver.memory": "8",
                "spark.executor.memory": "8"
            })

    def test_sparkJobWithJobConf(self):
        jobconf = ["--test.input='/data'", "--test.log=true", "-h", "--quiet"]
        sparkJob = SparkJob(self.uid, self.name, self.entrypoint, self.jar, self.options, jobconf)
        self.assertEqual(sparkJob.jobconf, jobconf)

    def test_convertToJson(self):
        sparkJob = SparkJob(self.uid, self.name, self.entrypoint, self.jar, self.options)
        obj = sparkJob.json()
        self.assertEqual(obj["uid"], self.uid)
        self.assertEqual(obj["name"], self.name)
        self.assertEqual(obj["entrypoint"], self.entrypoint)
        self.assertEqual(obj["jar"], self.jar)
        self.assertEqual(obj["options"], self.options)
        self.assertEqual(obj["jobconf"], [])

    def test_convertToDict(self):
        sparkJob = SparkJob(self.uid, self.name, self.entrypoint, self.jar, self.options)
        obj = sparkJob.dict()
        self.assertEqual(obj["uid"], self.uid)
        self.assertEqual(obj["name"], self.name)
        self.assertEqual(obj["entrypoint"], self.entrypoint)
        self.assertEqual(obj["jar"], self.jar)
        self.assertEqual(obj["options"], json.dumps(self.options))
        self.assertEqual(obj["jobconf"], json.dumps([]))

    def test_convertFromDict(self):
        sparkJob = SparkJob(self.uid, self.name, self.entrypoint, self.jar, self.options)
        obj = sparkJob.dict()
        newSparkJob = SparkJob.fromDict(obj)
        self.assertEqual(newSparkJob.uid, self.uid)
        self.assertEqual(newSparkJob.name, self.name)
        self.assertEqual(newSparkJob.entrypoint, self.entrypoint)
        self.assertEqual(newSparkJob.jar, self.jar)
        self.assertEqual(newSparkJob.options, self.options)
        self.assertEqual(newSparkJob.jobconf, [])

    def test_convertFromDictWithJobConf(self):
        jobconf = ["--test.input='/data'", "--test.log=true", "-h", "--quiet"]
        sparkJob = SparkJob(self.uid, self.name, self.entrypoint, self.jar, self.options, jobconf)
        obj = sparkJob.dict()
        newSparkJob = SparkJob.fromDict(obj)
        self.assertEqual(newSparkJob.uid, self.uid)
        self.assertEqual(newSparkJob.name, self.name)
        self.assertEqual(newSparkJob.entrypoint, self.entrypoint)
        self.assertEqual(newSparkJob.jar, self.jar)
        self.assertEqual(newSparkJob.options, self.options)
        self.assertEqual(newSparkJob.jobconf, jobconf)

    def test_execCommand(self):
        sparkJob = SparkJob(self.uid, self.name, self.entrypoint, self.jar, self.options)
        cmd = sparkJob.execCommand(self.masterurl, {SPARK_OCTOHAVEN_JOB_ID: sparkJob.uid})
        self.assertTrue(("%s=%s" % (SPARK_OCTOHAVEN_JOB_ID, sparkJob.uid)) in cmd)
        # increased number of parameters passed with spark uid key
        self.assertEqual(len(cmd), 18)

    def test_execCommandWithJobConf(self):
        jobconf = ["--test.input='/data'", "--test.log=true", "-h", "--quiet"]
        sparkJob = SparkJob(self.uid, self.name, self.entrypoint, self.jar, self.options, jobconf)
        cmd = sparkJob.execCommand(self.masterurl, {SPARK_OCTOHAVEN_JOB_ID: sparkJob.uid})
        self.assertTrue(("%s=%s" % (SPARK_OCTOHAVEN_JOB_ID, sparkJob.uid)) in cmd)
        # increased number of parameters passed with spark uid key
        self.assertEqual(len(cmd), 22)

# Load test suites
def _suites():
    return [
        SparkJobTestSuite
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
