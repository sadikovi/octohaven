#!/usr/bin/env python

import unittest
import os
from paths import ROOT_PATH
from src.sparkmodule import SparkModule, FREE, BUSY, DOWN

class SparkModuleTestSuite(unittest.TestCase):
    def setUp(self):
        self.master = "spark://jony.local-local:7077"
        self.ui = "http://test:8080"
        self.uiRun = "http://test:4040"

    def tearDown(self):
        pass

    def test_init(self):
        sparkModule = SparkModule(self.master, self.ui, self.uiRun)
        self.assertEqual(sparkModule.uiRunHost, "test")
        self.assertEqual(sparkModule.uiRunPort, 4040)

    def test_clusterInfo(self):
        sparkModule = SparkModule(self.master, self.ui, self.uiRun)
        apps = sparkModule.clusterInfo()
        self.assertEqual(apps, None)

    def test_clusterStatus(self):
        sparkModule = SparkModule(self.master, self.ui, self.uiRun)
        status = sparkModule.clusterStatus()
        self.assertEqual(status, DOWN)

    def test_runningApps(self):
        sparkModule = SparkModule(self.master, self.ui, self.uiRun)
        apps = sparkModule.runningApps()
        self.assertEqual(apps, None)

# Load test suites
def _suites():
    return [
        SparkModuleTestSuite
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
