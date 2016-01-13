#!/usr/bin/env python

import os, unittest, paths
from types import IntType, LongType, StringType
import src.octo.utils as utils

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

    def test_validateMemory(self):
        memory = ["8gb", "8g", "512mb", "512m", "1024M", "16G", "2pb"]
        for entry in memory:
            self.assertEqual(utils.validateMemory(entry), entry.lower())
        memory = ["16gigabytes", "16u", "320b", "gb", "mb"]
        for entry in memory:
            with self.assertRaises(StandardError):
                utils.validateMemory(entry)

    def test_validatePriority(self):
        self.assertEqual(utils.validatePriority(100), 100)
        self.assertEqual(utils.validatePriority(1), 1)
        self.assertEqual(utils.validatePriority(0), 0)
        with self.assertRaises(StandardError):
            utils.validatePriority(-1)
        with self.assertRaises(StandardError):
            utils.validatePriority({})

    def test_validateMasterUrl(self):
        master = ["spark://local:7077", "spark://chcs240.co.nz:7079", "spark://192.168.0.1:8080"]
        for entry in master:
            self.assertEqual(utils.validateMasterUrl(entry), entry)
        master = ["http://local:7077", "spark-local:7077"]
        for entry in master:
            with self.assertRaises(StandardError):
                utils.validateMasterUrl(entry)
        # check "as_uri_parts" flag
        self.assertEqual(utils.validateMasterUrl("spark://chcs240.co.nz:7079", as_uri_parts=True),
            ("spark://chcs240.co.nz:7079", "chcs240.co.nz", 7079))
        self.assertEqual(utils.validateMasterUrl("spark://192.168.0.1:8080", as_uri_parts=True),
            ("spark://192.168.0.1:8080", "192.168.0.1", 8080))

    def test_validateUiUrl(self):
        ui = ["http://localhost:8080", "http://sandbox:38080", "http://192.168.99.100:8080",
            "https://localhost:8081"]
        for entry in ui:
            self.assertEqual(utils.validateUiUrl(entry), entry)
        ui = ["https://localhost:", "http://192.168.99.100"]
        for entry in ui:
            with self.assertRaises(StandardError):
                utils.validateUiUrl(entry)
        # check "as_uri_parts" flag
        self.assertEqual(utils.validateUiUrl("http://192.168.99.100:8080", as_uri_parts=True),
            ("http://192.168.99.100:8080", "192.168.99.100", 8080))
        self.assertEqual(utils.validateUiUrl("https://sandbox:38080", as_uri_parts=True),
            ("https://sandbox:38080", "sandbox", 38080))

    def test_validateEntrypoint(self):
        entries = ["org.apache.spark.Test", "com.wyn.research.Test_core", "Test_core"]
        for entry in entries:
            self.assertEqual(utils.validateEntrypoint(entry), entry)
        entries = ["org-apache", "org.wrong.test.", "another.wrong.Test-test"]
        for entry in entries:
            with self.assertRaises(StandardError):
                utils.validateEntrypoint(entry)

    def test_validateJarPath(self):
        entries = [os.path.join(paths.ROOT_PATH, "test", "resources", "dummy.jar"),
            os.path.join(paths.ROOT_PATH, "absolute", "dummy.jar")]
        for entry in entries:
            self.assertEqual(utils.validateJarPath(entry), entry)
        entries = [os.path.join("local", "dummy.jar"),
            os.path.join("test", "resources", "dummy.jar")]
        for entry in entries:
            with self.assertRaises(StandardError):
                utils.validateJarPath(entry)

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
