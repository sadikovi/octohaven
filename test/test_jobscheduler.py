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

import unittest
from subprocess import Popen, PIPE
from src.scheduler import jobscheduler

class JobSchedulerTestSuite(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_updateProcessStatus(self):
        output = Popen(["ps", "-o", "pid="], stdout=PIPE)
        ls = output.communicate()[0]
        pid = ls.split()[0]
        wrong_pid = 99999
        self.assertEqual(jobscheduler.updateProcessStatus(None), 2)
        self.assertEqual(jobscheduler.updateProcessStatus(wrong_pid), 0)
        # return 0 because "ls" process is not spark-submit
        self.assertEqual(jobscheduler.updateProcessStatus(pid), 0)
        # test running process with SparkSubmit
        cmdList = ["/bin/bash", "-c",
            "while true; do echo org.apache.spark.deploy.SparkSubmit; sleep 10; done"]
        p1 = Popen(cmdList)
        try:
            self.assertEqual(jobscheduler.updateProcessStatus(p1.pid), -1)
        except Exception as e:
            print "[ERROR] Something bad happened while launching process p1: %s" % e.message
            self.assertEqual(False, True)
        finally:
            if p1:
                p1.kill()
            else:
                raise StandardError("[ERROR] Cannot kill infinite process. Please make sure " + \
                    "that it is not running, by using command [ps aux | grep -i while]")

# Load test suites
def _suites():
    return [
        JobSchedulerTestSuite
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
