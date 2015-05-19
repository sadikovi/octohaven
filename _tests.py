#!/usr/bin/env python

import _paths
import unittest

# select what tests to run
_RUN_TESTS = {
    "core":             False,
    "metastore":        True,
    "mysqlconnector":   True
}

def _checkTest(key):
    return key in _RUN_TESTS and _RUN_TESTS[key]

def _collectSystemTests(suites):
    # core
    if _checkTest("core"):
        import test.unittest_core as unittest_core
        suites.addTest(unittest_core.loadSuites())
    else:
        print "@skip: 'core' tests"

    # metastore
    if _checkTest("metastore"):
        import test.unittest_metastore as unittest_metastore
        suites.addTest(unittest_metastore.loadSuites())
    else:
        print "@skip: 'metastore' tests"

    # metastore
    if _checkTest("mysqlconnector"):
        import test.unittest_mysqlconnector as unittest_mysqlconnector
        suites.addTest(unittest_mysqlconnector.loadSuites())
    else:
        print "@skip: 'mysqlconnector' tests"

if __name__ == '__main__':
    suites = unittest.TestSuite()
    print ""
    print "### [:Octohaven] Gathering tests info ###"
    print "-" * 70
    _collectSystemTests(suites)
    print ""
    print "### [:Octohaven] Running tests ###"
    print "-" * 70
    unittest.TextTestRunner(verbosity=2).run(suites)
    num = len([x for x in _RUN_TESTS.values() if not x])
    print "%s Number of test blocks skipped: %d" %("OK" if num==0 else "WARN", num)
    print ""
