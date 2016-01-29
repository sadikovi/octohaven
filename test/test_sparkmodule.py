#!/usr/bin/env python

#
# Copyright 2015 sadikovi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os, unittest
from src.sparkmodule import SparkContext, FREE, BUSY, DOWN

class SparkModuleTestSuite(unittest.TestCase):
    def setUp(self):
        self.master = "spark://jony.local-local:7077"
        self.ui = "http://test:8080"
        self.uiRun = "http://test:4040"

    def tearDown(self):
        pass

    def test_init(self):
        sparkContext = SparkContext(self.master, self.ui, self.uiRun)
        self.assertEqual(sparkContext.uiRunHost, "test")
        self.assertEqual(sparkContext.uiRunPort, 4040)

    def test_clusterInfo(self):
        sparkContext = SparkContext(self.master, self.ui, self.uiRun)
        apps = sparkContext.clusterInfo()
        self.assertEqual(apps, None)

    def test_clusterStatus(self):
        sparkContext = SparkContext(self.master, self.ui, self.uiRun)
        status = sparkContext.clusterStatus()
        self.assertEqual(status, DOWN)

    def test_runningApps(self):
        sparkContext = SparkContext(self.master, self.ui, self.uiRun)
        apps = sparkContext.runningApps()
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
