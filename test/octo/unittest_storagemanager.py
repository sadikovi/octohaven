#!/usr/bin/env python

import unittest, test, src.octo.storagesetup as setup, src.octo.utils as utils
from src.octo.mysqlcontext import MySQLContext, MySQLLock
from src.octo.storagemanager import StorageManager

class StorageManagerTestSuite(unittest.TestCase):
    def setUp(self):
        config = {
            "host": test.Settings.mp().get("host"),
            "port": test.Settings.mp().get("port"),
            "user": test.Settings.mp().get("user"),
            "password": test.Settings.mp().get("password"),
            "database": test.Settings.mp().get("database")
        }
        MySQLLock.reset()
        self.sqlcnx = MySQLContext(**config)
        setup.loadTables(self.sqlcnx, drop_existing=True, logging=False)

    def tearDown(self):
        pass

    def test_init(self):
        with self.assertRaises(StandardError):
            StorageManager(None)
        with self.assertRaises(StandardError):
            StorageManager({})
        manager = StorageManager(self.sqlcnx)

    def test_createTemplate(self):
        manager = StorageManager(self.sqlcnx)
        data = {"name": "template1", "createtime": 1, "content": "content1"}
        manager.createTemplate(data["name"], data["createtime"], data["content"])
        rows = manager.getTemplates()
        self.assertEqual(len(rows), 1)

    def test_getTemplates(self):
        manager = StorageManager(self.sqlcnx)
        for i in xrange(10):
            data = {"name": "test%s" % (10-i), "createtime": (10-i), "content": "content%s" % i}
            manager.createTemplate(data["name"], data["createtime"], data["content"])
        rows = manager.getTemplates()
        # build expected list, note that it uses the same name prefix
        expected = sorted(map(lambda x: "test%s" % (10-x), range(10)))
        self.assertEqual(len(rows), 10)
        self.assertEqual(map(lambda x: x["name"], rows), expected)

    def test_getTemplate(self):
        manager = StorageManager(self.sqlcnx)
        data = {"name": "template1", "createtime": 1, "content": "content1"}
        uid = manager.createTemplate(data["name"], data["createtime"], data["content"])
        row = manager.getTemplate(uid)
        self.assertEqual(row["uid"], uid)
        self.assertEqual(row["name"], data["name"])
        self.assertEqual(row["createtime"], data["createtime"])
        self.assertEqual(row["content"], data["content"])

    def test_deleteTemplate(self):
        manager = StorageManager(self.sqlcnx)
        data = {"name": "template1", "createtime": 1, "content": "content1"}
        uid = manager.createTemplate(data["name"], data["createtime"], data["content"])
        row = manager.getTemplate(uid)
        self.assertEqual(row["uid"], uid)
        self.assertEqual(row["name"], data["name"])
        # delete template
        manager.deleteTemplate(uid)
        row = manager.getTemplate(uid)
        self.assertEqual(row, None)

# Load test suites
def _suites():
    return [
        StorageManagerTestSuite
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
