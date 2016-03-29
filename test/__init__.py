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

import sys, unittest, importlib

# select what tests to run
RUN_TESTS = {
    "utils": True,
    "sparkmodule": True,
    "fs": True,
    "cron": True,
    "template": True,
    "job": True,
    "timetable": True
}

# default empty test suite
suites = unittest.TestSuite()

def checkTest(key):
    return key in RUN_TESTS and RUN_TESTS[key]

# assume that test name is "test.test_$NAME", where $NAME is name of the module
def addTests2(name):
    addTests(name, "test.test_%s" % name)

# add individual test module
def addTests(name, moduleName):
    if checkTest(name):
        module = importlib.import_module(moduleName)
        suites.addTest(module.loadSuites())
    else:
        print "@skip: '%s' tests" % name

# collect all the tests in the system
def collectSystemTests(suites):
    addTests2("utils")
    addTests2("sparkmodule")
    addTests2("fs")
    addTests2("cron")
    addTests2("template")
    addTests2("job")
    addTests2("timetable")

def main(args=[]):
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
