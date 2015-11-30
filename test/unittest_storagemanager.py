#!/usr/bin/env python

import unittest
import uuid
import time
import random
from src.job import Job, STATUSES
from src.redisconnector import RedisConnectionPool, RedisConnector
from src.storagemanager import StorageManager, KeyspaceProvider
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

    def test_itemForUid(self):
        storageManager = StorageManager(self.connector)
        self.assertEqual(storageManager.itemForUid("None"), None)

    def test_saveItem(self):
        storageManager = StorageManager(self.connector)
        with self.assertRaises(StandardError):
            storageManager.saveItem(None)

    def test_saveAndRetrieveItem(self):
        storageManager = StorageManager(self.connector)
        job = self.newJob()
        storageManager.saveItem(job, klass=Job)
        retrieved = storageManager.itemForUid(job.uid, klass=Job)
        self.assertEqual(retrieved.toDict(), job.toDict())

    def test_itemsForKeyspace(self):
        storageManager = StorageManager(self.connector)
        job = self.newJob()
        jobs = storageManager.itemsForKeyspace(job.status, klass=Job)
        self.assertEqual(jobs, [])

    def test_addItemForStatus(self):
        storageManager = StorageManager(self.connector)
        job = self.newJob()
        storageManager.addItemToKeyspace(job.status, job.uid)
        # test correct retrieval
        storageManager.saveItem(job, klass=Job)
        jobs = storageManager.itemsForKeyspace(job.status, klass=Job)
        self.assertEqual(len(jobs), 1)

    def test_removeJobFromStatus(self):
        storageManager = StorageManager(self.connector)
        job = self.newJob()
        storageManager.removeItemFromKeyspace(job.status, job.uid)

    def test_manageJobs(self):
        storageManager = StorageManager(self.connector)
        jobs = [self.newJob() for i in range(10)]
        for job in jobs:
            storageManager.saveItem(job, klass=Job)
            storageManager.addItemToKeyspace(job.status, job.uid)
        allJobs = storageManager.itemsForKeyspace(jobs[0].status, klass=Job)
        self.assertEqual(sorted([a.uid for a in allJobs]), sorted([b.uid for b in jobs]))
        results = dict([(status, 0) for status in STATUSES])
        for job in jobs:
            if job.status in results:
                results[job.status] += 1
        for status in STATUSES:
            got = storageManager.itemsForKeyspace(status)
            self.assertEqual(len(got), results[status])

    def test_limitJobs(self):
        storageManager = StorageManager(self.connector)
        numJobs = 10
        jobs = [self.newJob() for i in range(numJobs)]
        for job in jobs:
            storageManager.saveItem(job, klass=Job)
            storageManager.addItemToKeyspace(job.status, job.uid)
        got = storageManager.itemsForKeyspace(job.status, limit=20, klass=Job)
        self.assertEqual(len(got), numJobs)
        got = storageManager.itemsForKeyspace(job.status, limit=-1, klass=Job)
        self.assertEqual(len(got), numJobs)
        got = storageManager.itemsForKeyspace(job.status, limit=3, klass=Job)
        self.assertEqual(len(got), 3)

    def test_addItemsToKeyspace(self):
        storageManager = StorageManager(self.connector)
        jobs = [self.newJob(), self.newJob()]
        storageManager.addItemsToKeyspace("multiplejobs", [x.uid for x in jobs])
        for job in jobs:
            storageManager.saveItem(job, klass=Job)
        savedJobs = storageManager.itemsForKeyspace("multiplejobs", klass=Job)
        self.assertEqual(sorted([x.uid for x in savedJobs]), sorted([x.uid for x in jobs]))

    def test_removeItemsFromKeyspace(self):
        storageManager = StorageManager(self.connector)
        jobs = [self.newJob(), self.newJob(), self.newJob()]
        storageManager.addItemsToKeyspace("multiplejobs", [x.uid for x in jobs])
        for job in jobs:
            storageManager.saveItem(job, klass=Job)
        storageManager.removeItemsFromKeyspace("multiplejobs", [x.uid for x in jobs][:2])
        leftJobs = storageManager.itemsForKeyspace("multiplejobs", klass=Job)
        self.assertEqual([x.uid for x in leftJobs], [x.uid for x in jobs][2:])

# dummy class A for testing
class A(KeyspaceProvider, object):
    pass
# dummy class B for testing
class B(KeyspaceProvider, object):
    pass

class KeyspaceProviderTestSuite(unittest.TestCase):
    def test_diffKeyspace(self):
        a = A()
        b = B()
        self.assertEqual(a.keyspace("test"), A.keyspace("test"))
        self.assertEqual(b.keyspace("test"), B.keyspace("test"))
        self.assertTrue(a.keyspace("test") != b.keyspace("test"))
        self.assertEqual(a.keyspace(None), a.keyspace("") + str(None))

    def test_sameKeyspace(self):
        a = A()
        b = A()
        self.assertEqual(a.keyspace("test"), b.keyspace("test"))
        self.assertEqual(a.keyspace(None), b.keyspace(None))

# Load test suites
def _suites():
    return [
        StorageManagerTestSuite,
        KeyspaceProviderTestSuite
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
