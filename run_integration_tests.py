#!/usr/bin/env python

import unittest
import paths
import sys

# select what tests to run
RUN_TESTS = {
    "api": True
}

def checkTest(key):
    return key in RUN_TESTS and RUN_TESTS[key]

def collectSystemTests(suites):
    # redis connector
    if checkTest("api"):
        import test.it.it_api as it_api
        suites.addTest(it_api.loadSuites())
    else:
        print "@skip: 'api' tests"

if __name__ == '__main__':
    args = sys.argv[2:]
    if not args or len(args) < 2:
        raise StandardError("Required: OCTOHAVEN_HOST, OCTOHAVEN_PORT, got %s" % args)
    else:
        from test.it.it_constants import Settings
        Settings.mp().set("host", args[0])
        Settings.mp().set("port", args[1])
    suites = unittest.TestSuite()
    print ""
    print "### [:Octohaven] Gathering tests info ###"
    print "-" * 70
    collectSystemTests(suites)
    print ""
    print "### [:Octohaven] Running integration tests ###"
    print "-" * 70
    # results is a TextTestRunner object that is used to define exit code of tests
    results = unittest.TextTestRunner(verbosity=2).run(suites)
    num = len([x for x in RUN_TESTS.values() if not x])
    print "%s Number of test blocks skipped: %d" %("OK" if num==0 else "WARN", num)
    print ""
    # fail if there is at least 1 error or failure
    if results and len(results.failures) == 0 and len(results.errors) == 0:
        sys.exit(0)
    else:
        sys.exit(1)
