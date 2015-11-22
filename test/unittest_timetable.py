#!/usr/bin/env python

import unittest
from src.timetable import Timetable, TimetableManager
from src.utils import *
from src.sparkmodule import SparkModule
from src.redisconnector import RedisConnectionPool, RedisConnector
from src.storagemanager import StorageManager
from src.jobmanager import JobManager, ALL_JOBS_KEY
from test.unittest_constants import RedisConst
from test.unittest_job import JobSentinel

class TimetableTestSuite(unittest.TestCase):
    def setUp(self):
        self.uid = nextTimetableId()
        self.name = "test-timetable"
        self.canceled = False
        self.clonejobid = nextJobId()
        self.starttime = currentTimeMillis()
        self.intervals = [120, 240, 120]
        self.jobs = [nextJobId(), nextJobId(), nextJobId()]

    def tearDown(self):
        pass

    def test_init(self):
        with self.assertRaises(StandardError):
            Timetable(self.uid, self.name, self.canceled, self.clonejobid, "time", self.intervals,
                self.jobs)
        with self.assertRaises(StandardError):
            Timetable(self.uid, self.name, self.canceled, self.clonejobid, self.starttime, {},
                self.jobs)
        with self.assertRaises(StandardError):
            Timetable(self.uid, self.name, self.canceled, self.clonejobid, self.starttime,
                self.intervals, None)
        timetable = Timetable(self.uid, self.name, self.canceled, self.clonejobid, self.starttime,
            self.intervals, self.jobs)
        self.assertEqual(timetable.numTotalJobs, 0)
        self.assertEqual(timetable.numJobs, len(self.jobs))
        self.assertEqual(timetable.jobs, self.jobs)

    def test_numJobs(self):
        jobs = Timetable.numJobs(10, [5, 5, 10, 20])
        self.assertEqual(jobs, 2)
        jobs = Timetable.numJobs(30, [5, 5, 10, 20])
        self.assertEqual(jobs, 3)
        jobs = Timetable.numJobs(50, [5, 5, 10, 20])
        self.assertEqual(jobs, 6)
        jobs = Timetable.numJobs(79, [5, 5, 10, 20])
        self.assertEqual(jobs, 7)
        jobs = Timetable.numJobs(80, [5, 5, 10, 20])
        self.assertEqual(jobs, 8)
        jobs = Timetable.numJobs(-100, [5, 5, 10, 20])
        self.assertEqual(jobs, 0)
        jobs = Timetable.numJobs(10, [])
        self.assertEqual(jobs, 0)
        jobs = Timetable.numJobs(10, [0])
        self.assertEqual(jobs, 0)
        jobs = Timetable.numJobs(0, [0])
        self.assertEqual(jobs, 0)

    def test_incrementJob(self):
        timetable = Timetable(self.uid, self.name, self.canceled, self.clonejobid, self.starttime,
            self.intervals, self.jobs)
        timetable.incrementJob("job_1")
        timetable.incrementJob("job_2")
        timetable.incrementJob("job_3")
        self.assertEqual(timetable.numTotalJobs, 3)
        self.assertEqual(timetable.numJobs, 6)
        # `self.jobs` is also updated as we pass it by reference and do not clone
        self.assertEqual(timetable.jobs, self.jobs)

    def test_toFromDict(self):
        timetable = Timetable(self.uid, self.name, self.canceled, self.clonejobid, self.starttime,
            self.intervals, self.jobs)
        obj = timetable.toDict()
        copy = Timetable.fromDict(obj)
        self.assertEqual(copy.uid, timetable.uid)
        self.assertEqual(copy.name, timetable.name)
        self.assertEqual(copy.canceled, timetable.canceled)
        self.assertEqual(copy.clonejobid, timetable.clonejobid)
        self.assertEqual(copy.starttime, timetable.starttime)
        self.assertEqual(copy.intervals, timetable.intervals)
        self.assertEqual(copy.numTotalJobs, 0)
        self.assertEqual(copy.numJobs, timetable.numJobs)
        self.assertEqual(copy.jobs, timetable.jobs)

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
        job = JobSentinel.job()
        name = "test_timetable"
        delay = 100 # delay in seconds
        intervals = [100, 200, 200, 50]
        timetable = manager.createTimetable(name, delay, intervals, job)
        self.assertEqual(timetable.name, name)
        self.assertTrue(timetable.starttime > currentTimeMillis() and
            timetable.starttime <= currentTimeMillis() + delay * 1000)
        self.assertEqual(timetable.clonejobid, job.uid)

    def test_saveAndLoadTimetable(self):
        manager = TimetableManager(self.jobManager)
        job = JobSentinel.job()
        name = "test_timetable"
        delay = 100 # delay in seconds
        intervals = [100, 200, 200, 50]
        timetable = manager.createTimetable(name, delay, intervals, job)
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
        job = JobSentinel.job()
        timetable = manager.createTimetable("test_timetable", 100, [100, 200, 200, 50], job)
        manager.saveTimetable(timetable)
        tables = manager.listTimetables()
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0].uid, timetable.uid)

    def test_cancel(self):
        manager = TimetableManager(self.jobManager)
        with self.assertRaises(StandardError):
            manager.cancel(None)
        job = JobSentinel.job()
        # try canceling timetable that is non-active
        timetable = manager.createTimetable("test_timetable", 100, [100, 200, 200, 50], job)
        timetable.canceled = True
        manager.saveTimetable(timetable)
        with self.assertRaises(StandardError):
            manager.cancel(timetable.uid)
        # try canceling timetable
        timetable = manager.createTimetable("test_timetable", 100, [100, 200, 200, 50], job)
        manager.saveTimetable(timetable)
        manager.cancel(timetable.uid)
        # retrieve saved timetable and check status
        updated = manager.timetableForUid(timetable.uid)
        self.assertEqual(type(updated), Timetable)
        self.assertEqual(updated.canceled, True)

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
