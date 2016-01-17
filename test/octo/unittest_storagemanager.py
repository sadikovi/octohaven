#!/usr/bin/env python

import unittest, test, src.octo.storagesetup as setup, src.octo.utils as utils
from src.octo.mysqlcontext import MySQLContext, MySQLLock
from src.octo.storagemanager import StorageManager
from src.octo.job import Job
from src.octo.sparkjob import SparkJob

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
        # for job tests
        self.now = utils.currentTimeMillis()
        self.jdict = {"uid": None, "name": "job", "status": "READY", "createtime": self.now,
            "submittime": self.now, "starttime": -1, "finishtime": -1, "sparkjob": None,
            "priority": 123, "sparkappid": None}
        self.sdict = {"uid": None, "name": "sparkjob", "entrypoint": "a.b.c", "jar": "test.jar",
            "options": "{\"test\": 12}", "jobconf": "[1, 2, 3]"}

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

    def test_createJob(self):
        manager = StorageManager(self.sqlcnx)
        uid = manager.createJob(self.sdict, self.jdict)
        row = manager.getJob(uid, withSparkJob=False)
        self.assertEqual(row["uid"], uid)
        self.assertEqual(row["name"], self.jdict["name"])
        self.assertEqual(row["status"], self.jdict["status"])
        self.assertEqual(row["createtime"], self.jdict["createtime"])

    def test_updateStatus(self):
        manager = StorageManager(self.sqlcnx)
        uid = manager.createJob(self.sdict, self.jdict)
        manager.updateStatus(uid, "CLOSED")
        row = manager.getJob(uid, withSparkJob=False)
        self.assertEqual(row["uid"], uid)
        self.assertEqual(row["status"], "CLOSED")

    def test_updateStatusAndFinishTime(self):
        manager = StorageManager(self.sqlcnx)
        uid = manager.createJob(self.sdict, self.jdict)
        manager.updateStatusAndFinishTime(uid, "FINISHED", self.now)
        row = manager.getJob(uid, withSparkJob=False)
        self.assertEqual(row["uid"], uid)
        self.assertEqual(row["status"], "FINISHED")
        self.assertEqual(row["finishtime"], self.now)

    def test_getJob(self):
        manager = StorageManager(self.sqlcnx)
        uid = manager.createJob(self.sdict, self.jdict)
        row = manager.getJob(uid, withSparkJob=True)
        # assert job
        self.assertEqual(row["uid"], uid)
        self.assertEqual(row["name"], self.jdict["name"])
        self.assertEqual(row["createtime"], self.jdict["createtime"])
        self.assertEqual(row["status"], self.jdict["status"])
        # assert Spark job
        self.assertEqual(row["spark_uid"], row["sparkjob"])
        self.assertEqual(row["spark_name"], self.sdict["name"])
        self.assertEqual(row["spark_entrypoint"], self.sdict["entrypoint"])

    def test_getJobsByCreateTime(self):
        manager = StorageManager(self.sqlcnx)
        # create jobs
        self.jdict["status"] = "READY"
        manager.createJob(self.sdict, self.jdict)
        self.jdict["status"] = "RUNNING"
        manager.createJob(self.sdict, self.jdict)
        self.jdict["status"] = "FINISHED"
        manager.createJob(self.sdict, self.jdict)
        # fetch jobs
        rows = manager.getJobsByCreateTime(limit=100)
        self.assertEqual(len(rows), 3)
        rows = manager.getJobsByCreateTime(limit=None)
        self.assertEqual(len(rows), 3)
        rows = manager.getJobsByCreateTime(limit=1)
        self.assertEqual(len(rows), 1)

    def test_getJobsByStatusCreateTime(self):
        manager = StorageManager(self.sqlcnx)
        # create jobs
        self.jdict["status"] = "READY"
        manager.createJob(self.sdict, self.jdict)
        self.jdict["status"] = "RUNNING"
        manager.createJob(self.sdict, self.jdict)
        self.jdict["status"] = "FINISHED"
        manager.createJob(self.sdict, self.jdict)
        manager.createJob(self.sdict, self.jdict)
        # fetch jobs
        rows = manager.getJobsByStatusCreateTime(status=None, limit=100)
        self.assertEqual(len(rows), 4)
        rows = manager.getJobsByStatusCreateTime(status="READY", limit=100)
        self.assertEqual(len(rows), 1)
        rows = manager.getJobsByStatusCreateTime(status="FINISHED", limit=100)
        self.assertEqual(len(rows), 2)

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
