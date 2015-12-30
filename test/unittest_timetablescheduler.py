#!/usr/bin/env python

import unittest
from src.redisconnector import RedisConnectionPool, RedisConnector
from src.timetablescheduler import TimetableScheduler
from unittest_constants import RedisConst

class TimetableSchedulerTestSuite(unittest.TestCase):
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
            tscheduler = TimetableScheduler({})
        tscheduler = TimetableScheduler(self.settings)
        self.assertEqual(tscheduler.pool, {})

# Load test suites
def _suites():
    return [
        TimetableSchedulerTestSuite
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
