#!/usr/bin/env python

import unittest
import paths
import sys

# select what tests to run
RUN_TESTS = {
    "redisconnector": True,
    "job": True
}

def checkTest(key):
    return key in RUN_TESTS and RUN_TESTS[key]

def collectSystemTests(suites):
    # redis connector
    if checkTest("redisconnector"):
        import test.unittest_redisconnector as unittest_redisconnector
        suites.addTest(unittest_redisconnector.loadSuites())
    else:
        print "@skip: 'redisconnector' tests"

    # job class
    if checkTest("job"):
        import test.unittest_job as unittest_job
        suites.addTest(unittest_job.loadSuites())
    else:
        print "@skip: 'job' tests"

if __name__ == '__main__':
    suites = unittest.TestSuite()
    print ""
    print "### [:Octohaven] Gathering tests info ###"
    print "-" * 70
    collectSystemTests(suites)
    print ""
    print "### [:Octohaven] Running tests ###"
    print "-" * 70
    unittest.TextTestRunner(verbosity=2).run(suites)
    num = len([x for x in RUN_TESTS.values() if not x])
    print "%s Number of test blocks skipped: %d" %("OK" if num==0 else "WARN", num)
    print ""
