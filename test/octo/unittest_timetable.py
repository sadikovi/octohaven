#!/usr/bin/env python

import unittest, src.octo.utils as utils
from src.octo.timetable import *
from src.octo.crontab import CronTab

class TimetableTestSuite(unittest.TestCase):
    def setUp(self):
        self.uid = 123
        self.name = "test-timetable"
        self.status = TIMETABLE_ACTIVE
        self.clonejob = 123
        self.crontab = CronTab.fromPattern("0 8-12 * * * *")
        self.starttime = utils.currentTimeMillis()
        self.stoptime = -1

    def tearDown(self):
        pass

    def test_init(self):
        with self.assertRaises(StandardError):
            Timetable(self.uid, self.name, self.status, self.clonejob, None, self.starttime,
                self.stoptime)
        with self.assertRaises(StandardError):
            Timetable(self.uid, self.name, "TEST", self.clonejob, self.crontab, self.starttime,
                self.stoptime)
        timetable = Timetable(self.uid, self.name, self.status, self.clonejob, self.crontab,
            self.starttime, self.stoptime)
        # test for empty name
        timetable = Timetable(self.uid, DEFAULT_TIMETABLE_NAME, self.status, self.clonejob,
            self.crontab, self.starttime, self.stoptime)
        self.assertEqual(timetable.name, DEFAULT_TIMETABLE_NAME)

    def test_toFromDict(self):
        timetable = Timetable(self.uid, self.name, self.status, self.clonejob, self.crontab,
            self.starttime, self.stoptime)
        obj = timetable.dict()
        copy = Timetable.fromDict(obj)
        self.assertEqual(copy.uid, timetable.uid)
        self.assertEqual(copy.name, timetable.name)
        self.assertEqual(copy.status, timetable.status)
        self.assertEqual(copy.clonejob, timetable.clonejob)
        self.assertEqual(copy.crontab.dict(), timetable.crontab.dict())
        self.assertEqual(copy.starttime, timetable.starttime)
        self.assertEqual(copy.stoptime, timetable.stoptime)

# Load test suites
def _suites():
    return [
        TimetableTestSuite
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
