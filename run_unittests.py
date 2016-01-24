#!/usr/bin/env python

import sys, unittest, importlib, paths, test
from cli import CLI

# select what tests to run
RUN_TESTS = {
    "utils": True,
    "mysqlcontext": True,
    "sparkmodule": True,
    "subscription": True,
    "crontab": True,
    "filemanager": True,
    "storagemanager": True,
    "template": True,
    "sparkjob": True,
    "job": True,
    "jobmanager": True,
    "timetable": True
}

def checkTest(key):
    return key in RUN_TESTS and RUN_TESTS[key]

# add individual test module
def addTests(name, moduleName):
    if checkTest(name):
        module = importlib.import_module(moduleName)
        suites.addTest(module.loadSuites())
    else:
        print "@skip: '%s' tests" % name

# collect all the tests in the system
def collectSystemTests(suites):
    addTests("utils", "test.octo.unittest_utils")
    addTests("sparkmodule", "test.octo.unittest_sparkmodule")
    addTests("subscription", "test.octo.unittest_subscription")
    addTests("mysqlcontext", "test.octo.unittest_mysqlcontext")
    addTests("crontab", "test.octo.unittest_crontab")
    addTests("filemanager", "test.octo.unittest_filemanager")
    addTests("storagemanager", "test.octo.unittest_storagemanager")
    addTests("template", "test.octo.unittest_template")
    addTests("sparkjob", "test.octo.unittest_sparkjob")
    addTests("job", "test.octo.unittest_job")
    addTests("jobmanager", "test.octo.unittest_jobmanager")
    addTests("timetable", "test.octo.unittest_timetable")

if __name__ == '__main__':
    cli = CLI(sys.argv[1:])
    # add shared connection settings
    test.Settings.mp().set("host", cli.get("host"))
    test.Settings.mp().set("port", cli.get("port"))
    test.Settings.mp().set("user", cli.get("user"))
    test.Settings.mp().set("password", cli.get("password"))
    test.Settings.mp().set("database", cli.get("database"))

    suites = unittest.TestSuite()
    print ""
    print "### [:Octohaven] Gathering tests info ###"
    print "-" * 70
    collectSystemTests(suites)
    print ""
    print "### [:Octohaven] Running tests ###"
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
