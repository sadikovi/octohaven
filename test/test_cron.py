#!/usr/bin/env python

import unittest, src.utils as utils
from datetime import datetime
from src.cron import CronExpression

class CronExpressionTestSuite(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_emptyPattern(self):
        cron = CronExpression.fromPattern("* * * * * *")
        self.assertEquals(cron.minute, None)
        self.assertEquals(cron.hour, None)
        self.assertEquals(cron.day, None)
        self.assertEquals(cron.month, None)
        self.assertEquals(cron.weekday, None)
        self.assertEquals(cron.year, None)

    def test_simplePattern(self):
        cron = CronExpression.fromPattern("0 9 * * * *")
        self.assertEquals(cron.minute, 0)
        self.assertEquals(cron.hour, 9)

        cron = CronExpression.fromPattern("0 9 1 * 1 2015")
        self.assertEquals(cron.minute, 0)
        self.assertEquals(cron.hour, 9)
        self.assertEquals(cron.day, 1)
        self.assertEquals(cron.weekday, 1)
        self.assertEquals(cron.year, 2015)

        # testing similar patterns
        one = CronExpression.fromPattern("59 23 31 12 5 *")
        two = CronExpression.fromPattern("59 23 31 DEC Fri *")
        self.assertEquals(one.minute, two.minute)
        self.assertEquals(one.hour, two.hour)
        self.assertEquals(one.day, two.day)
        self.assertEquals(one.month, two.month)
        self.assertEquals(one.weekday, two.weekday)
        self.assertEquals(one.year, two.year)

    def test_ranges(self):
        cron = CronExpression.fromPattern("0 0,12 1 */2 * *")
        self.assertEquals(cron.minute, 0)
        self.assertEquals(cron.hour, set([0, 12]))
        self.assertEquals(cron.day, 1)
        self.assertEquals(cron.month, set([2, 4, 6, 8, 10, 12]))
        self.assertEquals(cron.weekday, None)
        self.assertEquals(cron.year, None)

        cron = CronExpression.fromPattern("0,15,30,45 0,6,12,18 1,15,31 * 1-5 *")
        self.assertEquals(cron.minute, set([0, 15, 30, 45]))
        self.assertEquals(cron.hour, set([0, 6, 12, 18]))
        self.assertEquals(cron.day, set([1, 15, 31]))
        self.assertEquals(cron.month, None)
        self.assertEquals(cron.weekday, set([1, 2, 3, 4, 5]))
        self.assertEquals(cron.year, None)
        # the same as above
        cron = CronExpression.fromPattern("*/15 */6 1,15,31 * 1-5 *")
        self.assertEquals(cron.minute, set([0, 15, 30, 45]))
        self.assertEquals(cron.hour, set([0, 6, 12, 18]))
        self.assertEquals(cron.day, set([1, 15, 31]))
        self.assertEquals(cron.month, None)
        self.assertEquals(cron.weekday, set([1, 2, 3, 4, 5]))
        self.assertEquals(cron.year, None)

        cron = CronExpression.fromPattern("* 0-11 * * * *")
        self.assertEquals(cron.hour, set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]))
        cron = CronExpression.fromPattern("0 12 * * Mon-Fri *")
        self.assertEquals(cron.minute, 0)
        self.assertEquals(cron.hour, 12)
        self.assertEquals(cron.weekday, set([1, 2, 3, 4, 5]))

    def test_incorrectPattern(self):
        # short pattern
        with self.assertRaises(StandardError):
            CronExpression.fromPattern("* * * * *")
        # wrong range
        with self.assertRaises(StandardError):
            CronExpression.fromPattern("* 1,2,3-10 * * * *")
        # out of bound
        with self.assertRaises(StandardError):
            CronExpression.fromPattern("* * 0-10 * * 2015")
        # wrong alternative
        with self.assertRaises(StandardError):
            CronExpression.fromPattern("* * 1-31 Jan-Tes * 2015")
        # wrong integer
        with self.assertRaises(StandardError):
            CronExpression.fromPattern("t b 11 9 * 2015")

    def test_json(self):
        one = CronExpression.fromPattern("*/15 */6 1,15,31 * 1-5 *")
        two = one.json()
        self.assertEquals(one.minute, two["minute"])
        self.assertEquals(one.hour, two["hour"])
        self.assertEquals(one.day, two["day"])
        self.assertEquals(one.month, two["month"])
        self.assertEquals(one.weekday, two["weekday"])
        self.assertEquals(one.year, two["year"])

    def test_ismatch(self):
        cron = CronExpression.fromPattern("*/15 */6 3,15,31 3,8,10 1-5 *")
        date1 = datetime(2015, 8, 3, 6, 45)
        date2 = datetime(2015, 10, 15, 6, 30)
        date3 = datetime(2015, 3, 31, 18, 30)
        date4 = datetime(2015, 3, 20, 12, 0)
        date5 = datetime(2015, 4, 15, 18, 30)
        self.assertEquals(cron.ismatch(utils.dateToTimestamp(date1)), True)
        self.assertEquals(cron.ismatch(utils.dateToTimestamp(date2)), True)
        self.assertEquals(cron.ismatch(utils.dateToTimestamp(date3)), True)
        self.assertEquals(cron.ismatch(utils.dateToTimestamp(date4)), False)
        self.assertEquals(cron.ismatch(utils.dateToTimestamp(date5)), False)

    def test_stringPattern(self):
        with self.assertRaises(StandardError):
            CronExpression.fromPattern(123)
        with self.assertRaises(StandardError):
            CronExpression.fromPattern({"123": 123})
        with self.assertRaises(StandardError):
            CronExpression.fromPattern([123])

# Load test suites
def _suites():
    return [
        CronExpressionTestSuite
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
