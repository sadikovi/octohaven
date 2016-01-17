#!/usr/bin/env python

import unittest, test, src.octo.storagesetup as setup, src.octo.utils as utils
from src.octo.mysqlcontext import MySQLContext, MySQLLock
from src.octo.storagemanager import StorageManager
from src.octo.jobmanager import JobManager

class JobManagerTestSuite(unittest.TestCase):
    def setUp(self):
        config = {
            "host": test.Settings.mp().get("host"),
            "port": test.Settings.mp().get("port"),
            "user": test.Settings.mp().get("user"),
            "password": test.Settings.mp().get("password"),
            "database": test.Settings.mp().get("database")
        }
        MySQLLock.reset()
        sqlcnx = MySQLContext(**config)
        setup.loadTables(sqlcnx, drop_existing=True, logging=False)
        self.storageManager = StorageManager(sqlcnx)
        self.options = {
            "spark.driver.memory": "8g",
            "spark.executor.memory": "8g",
            "spark.shuffle.spill": "true",
            "spark.file.overwrite": "true",
            "spark.executor.extraJavaOptions": "-XX:+PrintGCDetails -XX:+PrintGCTimeStamps",
            "spark.driver.extraJavaOptions": "-Dfile.encoding=UTF-8 -Dsun.jnu.encoding=UTF-8"
        }
        self.optionsString = "--name \"test\" " + "--master local[4] " + \
            "--conf spark.driver.memory=8g " + "--conf spark.executor.memory=8g " + \
            "--conf spark.shuffle.spill=true " + \
            "--conf \"spark.executor.extraJavaOptions=-XX:+PrintGCDetails -XX:+PrintGCTimeStamps\" " + \
            "--conf \"spark.file.overwrite=true\" " + \
            "--conf \"spark.driver.extraJavaOptions=-Dfile.encoding=UTF-8 -Dsun.jnu.encoding=UTF-8\""

    def tearDown(self):
        pass

    def test_init(self):
        manager = JobManager(self.storageManager)
        self.assertEqual(manager.storage, self.storageManager)
        with self.assertRaises(StandardError):
            JobManager(None)

    def test_parseOptions(self):
        manager = JobManager(self.storageManager)
        options = manager.parseOptions(self.optionsString)
        for key in self.options.keys():
            self.assertEqual(options[key], self.options[key])

    def test_parseJobConf(self):
        manager = JobManager(self.storageManager)
        # removing quotes is kind of weird
        variations = ["", "ls -lh /data", "-h --ignore=\"some true\"", "\"some true\""]
        res = [[], ["ls", "-lh", "/data"], ["-h", "--ignore=some true"], ["some true"]]
        for index in range(len(variations)):
            jobconf = manager.parseJobConf(variations[index])
            self.assertEqual(jobconf, res[index])

    def test_createJob(self):
        pass

    def test_jobForUid(self):
        pass

    def test_closeJob(self):
        pass

    def test_jobs(self):
        pass

    def test_jobsForStatus(self):
        pass

    def test_finishJob(self):
        pass

# Load test suites
def _suites():
    return [
        JobManagerTestSuite
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
