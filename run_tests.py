#!/usr/bin/env python

import unittest
import paths
import sys

# select what tests to run
RUN_TESTS = {
    "redisconnector": True,
    "job": True,
    "storagemanager": True,
    "filemanager": True,
    "jobmanager": True,
    "utils": True,
    "sparkmodule": True,
    "template": True
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

    # file manager
    if checkTest("filemanager"):
        import test.unittest_filemanager as unittest_filemanager
        suites.addTest(unittest_filemanager.loadSuites())
    else:
        print "@skip: 'filemanager' tests"

    # job manager
    if checkTest("jobmanager"):
        import test.unittest_jobmanager as unittest_jobmanager
        suites.addTest(unittest_jobmanager.loadSuites())
    else:
        print "@skip: 'jobmanager' tests"

    # utils
    if checkTest("utils"):
        import test.unittest_utils as unittest_utils
        suites.addTest(unittest_utils.loadSuites())
    else:
        print "@skip: 'utils' tests"

    # sparkmodule
    if checkTest("sparkmodule"):
        import test.unittest_sparkmodule as unittest_sparkmodule
        suites.addTest(unittest_sparkmodule.loadSuites())
    else:
        print "@skip: 'sparkmodule' tests"

    # template
    if checkTest("template"):
        import test.unittest_template as unittest_template
        suites.addTest(unittest_template.loadSuites())
    else:
        print "@skip: 'template' tests"

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
