#!/usr/bin/env python

import unittest
import uuid
import time
import random
from src.job import Job, STATUSES
from src.redisconnector import RedisConnectionPool, RedisConnector
from src.storagemanager import StorageManager
from test.unittest_constants import RedisConst
from test.unittest_job import JobSentinel

class StorageManagerTestSuite(unittest.TestCase):
    def setUp(self):
        test_pool = RedisConnectionPool({
            "host": RedisConst.redisHost(),
            "port": RedisConst.redisPort(),
            "db": RedisConst.redisTestDb()
        })
        self.connector = RedisConnector(test_pool)
        self.connector.flushdb()

    def tearDown(self):
        self.connector.flushdb()
        self.connector = None

    def newJob(self):
        return JobSentinel.job()

    def test_init(self):
        storageManager = StorageManager(self.connector)
        self.assertEqual(storageManager.connector, self.connector)
        # should raise an error for wrong connector
        with self.assertRaises(StandardError):
            StorageManager(None)

    def test_jobForUid(self):
        storageManager = StorageManager(self.connector)
        self.assertEqual(storageManager.jobForUid("None"), None)

    def test_saveJob(self):
        storageManager = StorageManager(self.connector)
        with self.assertRaises(StandardError):
            storageManager.saveJob(None)

    def test_saveAndRetrieveJob(self):
        storageManager = StorageManager(self.connector)
        job = self.newJob()
        storageManager.saveJob(job)
        retrieved = storageManager.jobForUid(job.uid)
        self.assertEqual(retrieved.toDict(), job.toDict())

    def test_jobsForStatus(self):
        storageManager = StorageManager(self.connector)
        job = self.newJob()
        jobs = storageManager.jobsForStatus(job.status)
        self.assertEqual(jobs, [])

    def test_addJobForStatus(self):
        storageManager = StorageManager(self.connector)
        job = self.newJob()
        storageManager.addJobForStatus(job.status, job.uid)

    def test_removeJobFromStatus(self):
        storageManager = StorageManager(self.connector)
        job = self.newJob()
        storageManager.removeJobFromStatus(job.status, job.uid)

    def test_manageJobs(self):
        storageManager = StorageManager(self.connector)
        jobs = [self.newJob() for i in range(10)]
        for job in jobs:
            storageManager.saveJob(job)
            storageManager.addJobForStatus(job.status, job.uid)
        allJobs = storageManager.jobsForStatus(jobs[0].status)
        self.assertEqual(sorted([a.uid for a in allJobs]), sorted([b.uid for b in jobs]))
        results = dict([(status, 0) for status in STATUSES])
        for job in jobs:
            if job.status in results:
                results[job.status] += 1
        for status in STATUSES:
            got = storageManager.jobsForStatus(status)
            self.assertEqual(len(got), results[status])

    def test_limitJobs(self):
        storageManager = StorageManager(self.connector)
        numJobs = 10
        jobs = [self.newJob() for i in range(numJobs)]
        for job in jobs:
            storageManager.saveJob(job)
            storageManager.addJobForStatus(job.status, job.uid)
        got = storageManager.jobsForStatus(job.status, limit=20)
        self.assertEqual(len(got), numJobs)
        got = storageManager.jobsForStatus(job.status, limit=-1)
        self.assertEqual(len(got), numJobs)
        got = storageManager.jobsForStatus(job.status, limit=3)
        self.assertEqual(len(got), 3)

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
