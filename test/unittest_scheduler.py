#!/usr/bin/env python

import unittest, os
from src.redisconnector import RedisConnectionPool, RedisConnector
from src.scheduler import Scheduler
from src.job import Job
from unittest_constants import RedisConst
from unittest_job import JobSentinel

class SchedulerTestSuite(unittest.TestCase):
    def setUp(self):
        test_pool = RedisConnectionPool({
            "host": RedisConst.redisHost(),
            "port": RedisConst.redisPort(),
            "db": RedisConst.redisTestDb()
        })
        self.connector = RedisConnector(test_pool)
        self.connector.flushdb()
        self.settings = {
            "REDIS_HOST": RedisConst.redisHost(),
            "REDIS_PORT": RedisConst.redisPort(),
            "REDIS_DB": RedisConst.redisTestDb(),
            "SPARK_UI_ADDRESS": "http://localhost:8080",
            "SPARK_UI_RUN_ADDRESS": "http://localhost:4040",
            "SPARK_MASTER_ADDRESS": "spark://localhost:7077"
        }

    def tearDown(self):
        self.connector = None

    def test_init(self):
        with self.assertRaises(StandardError):
            scheduler = Scheduler({})
        scheduler = Scheduler(self.settings)
        self.assertEqual(scheduler.poolSize, 5)
        self.assertEqual(scheduler.isRunning, False)

    def test_fetchStatus(self):
        job1 = JobSentinel.job()
        job2 = JobSentinel.job()
        # set entry point
        now = job1.createtime
        status = job1.status
        job1.submittime = now + 100
        job2.submittime = now + 30
        job1.createtime = now
        job2.createtime = now + 10
        scheduler = Scheduler(self.settings)
        scheduler.storageManager.saveItem(job1, klass=Job)
        scheduler.storageManager.saveItem(job2, klass=Job)
        scheduler.storageManager.addItemToKeyspace(status, job1.uid)
        scheduler.storageManager.addItemToKeyspace(status, job2.uid)
        jobs = scheduler.fetchStatus(status, -1)
        self.assertEqual(len(jobs), 2)
        self.assertEqual([x.uid for x in jobs], [job2.uid, job1.uid])

    def test_add(self):
        job1 = JobSentinel.job()
        job2 = JobSentinel.job()
        scheduler = Scheduler(self.settings)
        scheduler.add(job1, job1.priority)
        self.assertEqual(scheduler.pool.qsize(), 1)
        scheduler.add(job2, job2.priority)
        self.assertEqual(scheduler.pool.qsize(), 2)
        # insert the same job again but with different priority
        scheduler.add(job2, 1)
        self.assertEqual(scheduler.pool.qsize(), 2)

    def test_get(self):
        job1 = JobSentinel.job()
        job2 = JobSentinel.job()
        scheduler = Scheduler(self.settings)
        scheduler.add(job1, job1.priority)
        scheduler.add(job2, job2.priority)
        while scheduler.hasNext():
            self.assertEqual(type(scheduler.get()), Job)

# Load test suites
def _suites():
    return [
        SchedulerTestSuite
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
