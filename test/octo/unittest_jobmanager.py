#!/usr/bin/env python

import unittest, test, time, src.octo.storagesetup as setup, src.octo.utils as utils
from mysql.connector.errors import Error as SQLGlobalError
from src.octo.mysqlcontext import MySQLContext, MySQLLock
from src.octo.storagemanager import StorageManager
from src.octo.job import Job, CLOSED, READY, FINISHED, RUNNING
from src.octo.jobmanager import JobManager, JOB_DEFAULT_NAME

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
        # job options
        self.name = "test-job"
        self.delay = 0
        self.entrypoint = "a.b.c"
        self.jar = "/jars/test.jar"
        self.driverMemory = "8g"
        self.executorMemory = "8g"
        self.jobconf = "--conf a=true --conf b=false"

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
        manager = JobManager(self.storageManager)
        a = manager.createJob(self.name, self.delay, self.entrypoint, self.jar, self.driverMemory,
            self.executorMemory, self.optionsString, self.jobconf)
        job, sparkjob = manager.jobForUid(a.uid)
        self.assertNotEqual(job, None)
        self.assertNotEqual(sparkjob, None)
        self.assertEqual(a.sparkjob, sparkjob.uid)
        self.assertEqual(job.sparkjob, sparkjob.uid)
        self.assertEqual(job.name, self.name)
        self.assertEqual(sparkjob.options, self.options)
        # create job with default name
        a = manager.createJob("   ", self.delay, self.entrypoint, self.jar, self.driverMemory,
            self.executorMemory, self.optionsString, self.jobconf)
        job, sparkjob = manager.jobForUid(a.uid, False)
        self.assertNotEqual(job, None)
        self.assertEqual(sparkjob, None)
        self.assertEqual(job.name, JOB_DEFAULT_NAME)
        with self.assertRaises(StandardError):
            manager.createJob(self.name, self.delay, self.entrypoint, self.jar, "8", "8",
                self.optionsString, self.jobconf)
        # test submit time of the job with delay
        a = manager.createJob(self.name, 60, self.entrypoint, self.jar, self.driverMemory,
            self.executorMemory, self.optionsString, self.jobconf)
        job, sparkjob = manager.jobForUid(a.uid)
        self.assertTrue(job.submittime > utils.currentTimeMillis() + 50 * 1000L)

    def test_jobForUid(self):
        manager = JobManager(self.storageManager)
        a = manager.createJob(self.name, self.delay, self.entrypoint, self.jar, self.driverMemory,
            self.executorMemory, self.optionsString, self.jobconf)
        job, sparkjob = manager.jobForUid(a.uid, True)
        self.assertNotEqual(job, None)
        self.assertEqual(job.uid, a.uid)
        self.assertNotEqual(sparkjob, None)
        self.assertEqual(job.sparkjob, sparkjob.uid)
        # only job
        job, sparkjob = manager.jobForUid(a.uid, False)
        self.assertNotEqual(job, None)
        self.assertEqual(sparkjob, None)
        self.assertEqual(job.uid, a.uid)
        # neither job or sparkjob
        job, sparkjob = manager.jobForUid(-100 * a.uid, True)
        self.assertEqual(job, None)
        self.assertEqual(sparkjob, None)
        # should fail for non-integer uids
        with self.assertRaises(SQLGlobalError):
            manager.jobForUid("%s-test" % a.uid, True)

    def test_closeJob(self):
        manager = JobManager(self.storageManager)
        a = manager.createJob(self.name, self.delay, self.entrypoint, self.jar, self.driverMemory,
            self.executorMemory, self.optionsString, self.jobconf)
        self.assertEqual(a.status, READY)
        manager.closeJob(a)
        self.assertEqual(a.status, CLOSED)
        with self.assertRaises(StandardError):
            manager.closeJob(a)
        with self.assertRaises(StandardError):
            a.status = FINISHED
            manager.closeJob(a)
        with self.assertRaises(StandardError):
            a.uid = -1000
            manager.closeJob(a)

    def test_jobs(self):
        manager = JobManager(self.storageManager)
        manager.createJob(self.name, self.delay, self.entrypoint, self.jar, self.driverMemory,
            self.executorMemory, self.optionsString, self.jobconf)
        time.sleep(0.3)
        manager.createJob(self.name, self.delay, self.entrypoint, self.jar, self.driverMemory,
            self.executorMemory, self.optionsString, self.jobconf)
        time.sleep(0.3)
        manager.createJob(self.name, self.delay, self.entrypoint, self.jar, self.driverMemory,
            self.executorMemory, self.optionsString, self.jobconf)
        jobs = manager.jobs()
        self.assertEqual(len(jobs), 3)
        for job in jobs:
            self.assertEqual(type(job), Job)
        self.assertEqual([job.uid for job in jobs], [3, 2, 1])
        # test limit
        jobs = manager.jobs(2)
        self.assertEqual(len(jobs), 2)
        self.assertEqual([job.uid for job in jobs], [3, 2])

    def test_jobsForStatus(self):
        manager = JobManager(self.storageManager)
        a1 = manager.createJob(self.name, self.delay, self.entrypoint, self.jar, self.driverMemory,
            self.executorMemory, self.optionsString, self.jobconf)
        time.sleep(0.3)
        a2 = manager.createJob(self.name, self.delay, self.entrypoint, self.jar, self.driverMemory,
            self.executorMemory, self.optionsString, self.jobconf)
        time.sleep(0.3)
        a3 = manager.createJob(self.name, self.delay, self.entrypoint, self.jar, self.driverMemory,
            self.executorMemory, self.optionsString, self.jobconf)
        time.sleep(0.3)
        a4 = manager.createJob(self.name, self.delay, self.entrypoint, self.jar, self.driverMemory,
            self.executorMemory, self.optionsString, self.jobconf)
        # operations on jobs
        manager.closeJob(a1)
        a2.updateStatus(RUNNING)
        manager.finishJob(a2)
        # tests
        with self.assertRaises(StandardError):
            jobs = manager.jobsForStatus(None)
        jobs = manager.jobsForStatus(READY)
        self.assertEqual(len(jobs), 2)
        self.assertEqual([job.uid for job in jobs], [a4.uid, a3.uid])
        jobs = manager.jobsForStatus(FINISHED)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].uid, a2.uid)
        jobs = manager.jobsForStatus(CLOSED)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].uid, a1.uid)

    def test_finishJob(self):
        manager = JobManager(self.storageManager)
        a = manager.createJob(self.name, self.delay, self.entrypoint, self.jar, self.driverMemory,
            self.executorMemory, self.optionsString, self.jobconf)
        with self.assertRaises(StandardError):
            manager.finishJob(a)
        a.updateStatus(RUNNING)
        manager.finishJob(a)
        job, _ = manager.jobForUid(a.uid)
        self.assertEqual(a.status, FINISHED)
        self.assertEqual(job.status, FINISHED)
        self.assertEqual(a.dict(), job.dict())
        self.assertTrue(job.createtime < job.finishtime)

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
