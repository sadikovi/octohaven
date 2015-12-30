#!/usr/bin/env python

import unittest, os
from subprocess import Popen, PIPE
from src.redisconnector import RedisConnectionPool, RedisConnector
from src.scheduler import Scheduler, Link
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
        self.assertEqual(scheduler.forceSparkMasterAddress, False)
        # update settings to include "force-master-address" option
        self.settings["FORCE_SPARK_MASTER_ADDRESS"] = True
        scheduler = Scheduler(self.settings)
        self.assertEqual(scheduler.forceSparkMasterAddress, True)

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
        scheduler.updateJob(job1, status, job1.priority)
        scheduler.updateJob(job2, status, job2.priority)
        jobs = scheduler.jobsForStatus(status, -1)
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
        scheduler.add(job1, 100)
        scheduler.add(job2, 101)
        jobids, i = [job1.uid, job2.uid], 0
        while scheduler.hasNext():
            link = scheduler.nextLink()
            self.assertEqual(type(link), Link)
            self.assertEqual(link.jobid, jobids[i])
            i += 1

    def test_updateProcessStatus(self):
        output = Popen(["ps", "-o", "pid="], stdout=PIPE)
        ls = output.communicate()[0]
        pid = ls.split()[0]
        wrong_pid = 99999
        scheduler = Scheduler(self.settings)
        self.assertEqual(scheduler.updateProcessStatus(None), 2)
        self.assertEqual(scheduler.updateProcessStatus(wrong_pid), 0)
        # return 0 because "ls" process is not spark-submit
        self.assertEqual(scheduler.updateProcessStatus(pid), 0)
        # test running process with SparkSubmit
        cmdList = ["/bin/bash", "-c",
            "while true; do echo org.apache.spark.deploy.SparkSubmit; sleep 10; done"]
        p1 = Popen(cmdList)
        try:
            self.assertEqual(scheduler.updateProcessStatus(p1.pid), -1)
        except Exception as e:
            print "[ERROR] Something bad happened while launching process p1: %s" % e.message
            self.assertEqual(False, True)
        finally:
            if p1:
                p1.kill()
            else:
                raise StandardError("[ERROR] Cannot kill infinite process. Please make sure " + \
                    "that it is not running, by using command [ps aux | grep -i while]")

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
