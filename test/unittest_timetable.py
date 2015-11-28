#!/usr/bin/env python

import unittest
from src.timetable import *
from src.utils import *
from src.sparkmodule import SparkModule
from src.redisconnector import RedisConnectionPool, RedisConnector
from src.storagemanager import StorageManager
from src.jobmanager import JobManager, ALL_JOBS_KEY
from src.crontab import CronTab
from test.unittest_constants import RedisConst
from test.unittest_job import JobSentinel

class TimetableTestSuite(unittest.TestCase):
    def setUp(self):
        self.uid = nextTimetableId()
        self.name = "test-timetable"
        self.status = TIMETABLE_ACTIVE
        self.clonejobid = nextJobId()
        self.crontab = CronTab.fromPattern("0 8-12 * * * *")
        self.starttime = currentTimeMillis()
        self.stoptime = -1
        self.jobs = [nextJobId(), nextJobId(), nextJobId()]

    def tearDown(self):
        pass

    def test_init(self):
        with self.assertRaises(StandardError):
            Timetable(self.uid, self.name, self.status, self.clonejobid, None, self.starttime,
                self.stoptime, self.jobs)
        with self.assertRaises(StandardError):
            Timetable(self.uid, self.name, "TEST", self.clonejobid, self.crontab, self.starttime,
                self.stoptime, self.jobs)
        with self.assertRaises(StandardError):
            Timetable(self.uid, self.name, self.status, self.clonejobid, self.crontab,
                self.starttime, self.stoptime, {})
        timetable = Timetable(self.uid, self.name, self.status, self.clonejobid, self.crontab,
            self.starttime, self.stoptime, self.jobs)
        self.assertEqual(timetable.numJobs, len(self.jobs))
        self.assertEqual(timetable.jobs, self.jobs)
        # test for empty name
        timetable = Timetable(self.uid, "", self.status, self.clonejobid, self.crontab,
            self.starttime, self.stoptime, self.jobs)
        self.assertEqual(timetable.name, DEFAULT_TIMETABLE_NAME)

    def test_incrementJob(self):
        timetable = Timetable(self.uid, self.name, self.status, self.clonejobid, self.crontab,
            self.starttime, self.stoptime, self.jobs)
        with self.assertRaises(StandardError):
            timetable.addJob("job_1")
        timetable.addJob(JobSentinel.job())
        timetable.addJob(JobSentinel.job())
        self.assertEqual(timetable.numJobs, 5)
        self.assertEqual(len(timetable.jobs), 5)

    def test_updateLatestRunTime(self):
        timetable = Timetable(self.uid, self.name, self.status, self.clonejobid, self.crontab,
            self.starttime, self.stoptime, self.jobs)
        self.assertEqual(timetable.latestruntime, -1L)
        ts = currentTimeMillis()
        timetable.updateRunTime(ts)
        self.assertEqual(timetable.latestruntime, ts)

    def test_toFromDict(self):
        timetable = Timetable(self.uid, self.name, self.status, self.clonejobid, self.crontab,
            self.starttime, self.stoptime, self.jobs, currentTimeMillis())
        obj = timetable.toDict()
        copy = Timetable.fromDict(obj)
        self.assertEqual(copy.uid, timetable.uid)
        self.assertEqual(copy.name, timetable.name)
        self.assertEqual(copy.status, timetable.status)
        self.assertEqual(copy.clonejobid, timetable.clonejobid)
        self.assertEqual(copy.crontab.toDict(), timetable.crontab.toDict())
        self.assertEqual(copy.starttime, timetable.starttime)
        self.assertEqual(copy.stoptime, timetable.stoptime)
        self.assertEqual(copy.numJobs, timetable.numJobs)
        self.assertEqual(copy.jobs, timetable.jobs)
        self.assertTrue(copy.latestruntime is not None and
            copy.latestruntime == timetable.latestruntime)

class TimetableManagerTestSuite(unittest.TestCase):
    def setUp(self):
        # we do not validate spark master address, as it is part of the JobCheck tests
        test_pool = RedisConnectionPool({
            "host": RedisConst.redisHost(),
            "port": RedisConst.redisPort(),
            "db": RedisConst.redisTestDb()
        })
        self.connector = RedisConnector(test_pool)
        self.connector.flushdb()
        self.masterurl = "spark://jony-local.local:7077"
        self.uiurl = "http://localhost:8080"
        self.uiRunUrl = "http://localhost:4040"
        # create Spark module and storage manager for job manager
        self.sparkModule = SparkModule(self.masterurl, self.uiurl, self.uiRunUrl)
        self.storageManager = StorageManager(self.connector)
        self.jobManager = JobManager(self.sparkModule, self.storageManager)
        # timetable settings
        self.name = "test-timetable"
        self.clonejob = JobSentinel.job()
        self.crontab = CronTab.fromPattern("0 8-12 * * * *")

    def tearDown(self):
        pass

    def test_init(self):
        with self.assertRaises(StandardError):
            TimetableManager(None)
        manager = TimetableManager(self.jobManager)
        self.assertEqual(manager.storageManager, self.storageManager)

    def test_cloneSparkJob(self):
        manager = TimetableManager(self.jobManager)
        with self.assertRaises(StandardError):
            manager.cloneSparkJob(None)
        sparkjob = JobSentinel.sparkJob()
        copy = manager.cloneSparkJob(sparkjob)
        self.assertTrue(copy.uid != sparkjob.uid)
        copy.uid = None
        sparkjob.uid = None
        self.assertEqual(copy.toDict(), sparkjob.toDict())

    def test_cloneJob(self):
        manager = TimetableManager(self.jobManager)
        with self.assertRaises(StandardError):
            manager.cloneJob(None)
        job = JobSentinel.job()
        copy = manager.cloneJob(job)
        self.assertTrue(copy.uid != job.uid)
        self.assertTrue(copy != job)

    def test_createTimetable(self):
        manager = TimetableManager(self.jobManager)
        timetable = manager.createTimetable(self.name, self.crontab, self.clonejob)
        self.assertEqual(timetable.name, self.name)
        self.assertTrue(timetable.starttime <= currentTimeMillis() and
            timetable.starttime > currentTimeMillis() - 5000)
        self.assertEqual(timetable.clonejobid, self.clonejob.uid)

    def test_saveAndLoadTimetable(self):
        manager = TimetableManager(self.jobManager)
        timetable = manager.createTimetable(self.name, self.crontab, self.clonejob)
        with self.assertRaises(StandardError):
            manager.saveTimetable(None)
        manager.saveTimetable(timetable)
        saved = manager.timetableForUid(timetable.uid)
        self.assertEqual(type(saved), Timetable)
        self.assertEqual(saved.toDict(), timetable.toDict())

    def test_timetableForUid(self):
        manager = TimetableManager(self.jobManager)
        saved = manager.timetableForUid(None)
        self.assertEqual(saved, None)

    def test_listTimetables(self):
        manager = TimetableManager(self.jobManager)
        table1 = manager.createTimetable(self.name, self.crontab, self.clonejob)
        table2 = manager.createTimetable(self.name, self.crontab, self.clonejob)
        manager.saveTimetable(table1)
        manager.saveTimetable(table2)
        # request timetables
        tables = manager.listTimetables()
        self.assertEqual(len(tables), 2)
        self.assertEqual(sorted([x.uid for x in tables]), sorted([table1.uid, table2.uid]))

    def test_listTimetablesByStatus(self):
        manager = TimetableManager(self.jobManager)
        table1 = manager.createTimetable(self.name, self.crontab, self.clonejob)
        table1.status = TIMETABLE_ACTIVE
        manager.saveTimetable(table1)
        table2 = manager.createTimetable(self.name, self.crontab, self.clonejob)
        table2.status = TIMETABLE_PAUSED
        manager.saveTimetable(table2)
        table3 = manager.createTimetable(self.name, self.crontab, self.clonejob)
        manager.saveTimetable(table3)
        manager.cancel(table3)
        # fetch non canceled timetables
        arr = manager.listTimetables([TIMETABLE_ACTIVE, TIMETABLE_PAUSED])
        self.assertEqual(len(arr), 2)
        self.assertEqual(sorted([x.status for x in arr]),
            sorted([TIMETABLE_ACTIVE, TIMETABLE_PAUSED]))
        # fetch only active jobs
        arr = manager.listTimetables([TIMETABLE_ACTIVE])
        self.assertEqual(len(arr), 1)
        self.assertEqual(sorted([x.status for x in arr]), sorted([TIMETABLE_ACTIVE]))
        # fetch canceled jobs
        arr = manager.listTimetables([TIMETABLE_CANCELED])
        self.assertEqual(len(arr), 1)
        self.assertEqual(sorted([x.status for x in arr]), sorted([TIMETABLE_CANCELED]))
        # fail to fetch, if statuses is not a list
        with self.assertRaises(StandardError):
            manager.listTimetables(None)

    def test_resume(self):
        manager = TimetableManager(self.jobManager)
        timetable = manager.createTimetable(self.name, self.crontab, self.clonejob)
        timetable.status = TIMETABLE_ACTIVE
        with self.assertRaises(StandardError):
            manager.resume(timetable)
        timetable.status = TIMETABLE_CANCELED
        with self.assertRaises(StandardError):
            manager.resume(timetable)
        timetable.status = TIMETABLE_PAUSED
        manager.resume(timetable)
        # check that status is active
        timetable = manager.timetableForUid(timetable.uid)
        self.assertEqual(timetable.status, TIMETABLE_ACTIVE)

    def test_pause(self):
        manager = TimetableManager(self.jobManager)
        timetable = manager.createTimetable(self.name, self.crontab, self.clonejob)
        timetable.status = TIMETABLE_PAUSED
        with self.assertRaises(StandardError):
            manager.pause(timetable)
        timetable.status = TIMETABLE_CANCELED
        with self.assertRaises(StandardError):
            manager.pause(timetable)
        timetable.status = TIMETABLE_ACTIVE
        manager.pause(timetable)
        # check that status is paused
        timetable = manager.timetableForUid(timetable.uid)
        self.assertEqual(timetable.status, TIMETABLE_PAUSED)

    def test_cancel(self):
        manager = TimetableManager(self.jobManager)
        timetable = manager.createTimetable(self.name, self.crontab, self.clonejob)
        timetable.status = TIMETABLE_CANCELED
        with self.assertRaises(StandardError):
            manager.cancel(timetable)
        timetable.status = TIMETABLE_ACTIVE
        manager.cancel(timetable)
        # check that status is canceled and stop time is filled in
        canceled = manager.timetableForUid(timetable.uid)
        self.assertEqual(canceled.uid, timetable.uid)
        self.assertEqual(canceled.starttime, timetable.starttime)
        self.assertTrue(canceled.stoptime >= currentTimeMillis() - 5000 and
            canceled.stoptime <= currentTimeMillis())
        self.assertEqual(canceled.status, TIMETABLE_CANCELED)

# Load test suites
def _suites():
    return [
        TimetableTestSuite,
        TimetableManagerTestSuite
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
