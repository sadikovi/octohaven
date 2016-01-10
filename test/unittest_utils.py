#!/usr/bin/env python

import unittest
from types import IntType, LongType, StringType
import src.utils as utils

class UtilsTestSuite(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_jsonOrElse(self):
        self.assertEqual(utils.jsonOrElse("", None), None)
        self.assertEqual(utils.jsonOrElse("{}", None), {})
        self.assertEqual(utils.jsonOrElse("{\"key\": 1}", None), {"key": 1})
        self.assertEqual(utils.jsonOrElse("{\"key\":}", None), None)
        self.assertEqual(utils.jsonOrElse("[{\"a\": 1}, {\"b\": {\"c\": 2}}]", None),
            [{"a": 1}, {"b": {"c": 2}}])

    def test_intOrElse(self):
        self.assertEqual(utils.intOrElse("1", -1), 1)
        self.assertEqual(utils.intOrElse("1abs", -1), -1)
        self.assertEqual(utils.intOrElse("", -1), -1)

    def test_boolOrElse(self):
        self.assertEqual(utils.boolOrElse("true", False), True)
        self.assertEqual(utils.boolOrElse("yes", False), True)
        self.assertEqual(utils.boolOrElse("1", False), True)
        self.assertEqual(utils.boolOrElse("false", True), False)
        self.assertEqual(utils.boolOrElse("0", True), False)
        self.assertEqual(utils.boolOrElse("no", True), False)

    def test_assert(self):
        with self.assertRaises(StandardError):
            utils.assertType(1, StringType)
        with self.assertRaises(StandardError):
            utils.assertType(1, LongType)
        utils.assertType(1L, LongType)
        utils.assertType(1, IntType)
        utils.assertType("1L", StringType)

    def test_assertInstance(self):
        with self.assertRaises(StandardError):
            utils.assertInstance(1, StringType)
        with self.assertRaises(StandardError):
            utils.assertInstance(1, LongType)
        utils.assertInstance(1L, LongType)
        utils.assertInstance("1L", StringType)
        utils.assertInstance("1L", object)

# Load test suites
def _suites():
    return [
        UtilsTestSuite
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
