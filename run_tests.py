#!/usr/bin/env python

import unittest
import paths
import sys

# select what tests to run
RUN_TESTS = {
    "redisconnector": True,
    "job": True,
    "storagemanager": True
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

    # storage manager
    if checkTest("storagemanager"):
        import test.unittest_storagemanager as unittest_storagemanager
        suites.addTest(unittest_storagemanager.loadSuites())
    else:
        print "@skip: 'storagemanager' tests"

if __name__ == '__main__':
    args = sys.argv[2:]
    if not args or len(args) < 3:
        raise StandardError("Required: REDIS_HOST, REDIS_PORT, REDIS_TEST_DB, got %s" % args)
    else:
        from test.unittest_constants import RedisConst
        RedisConst.setRedisSettings(args[0], args[1], args[2])
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
