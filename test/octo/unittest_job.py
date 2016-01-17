#!/usr/bin/env python

import unittest, time, random, src.octo.utils as utils
from src.octo.job import *

class JobTestSuite(unittest.TestCase):
    def setUp(self):
        self.uid = 1234567
        self.name = "test-job"
        self.status = READY
        self.createtime = long(time.time())
        self.submittime = long(time.time())
        self.sparkjob = 1234567

    def tearDown(self):
        pass

    def test_create(self):
        job = Job(self.uid, self.name, self.status, self.createtime, self.submittime, self.sparkjob)
        self.assertEqual(job.uid, self.uid)
        self.assertEqual(job.name, self.name)
        self.assertEqual(job.status, self.status)
        self.assertEqual(job.createtime, self.createtime)
        self.assertEqual(job.submittime, self.submittime)
        self.assertEqual(job.sparkjob, self.sparkjob)
        # default priority should be resolved into submittime
        self.assertEqual(job.priority, self.submittime)
        # now if you specify priority defferent from DEFAULT_PRIORITY, it will be assigned
        job = Job(self.uid, self.name, self.status, self.createtime, self.submittime,
            self.sparkjob, priority=99)
        self.assertEqual(job.priority, 99)
        # check passing wrong status
        with self.assertRaises(StandardError):
            Job(self.uid, self.name, "WRONG_STATUS", self.createtime, self.submittime,
                self.sparkjob)

    def test_validateStatus(self):
        status = random.choice(STATUSES)
        self.assertEqual(Job.checkStatus(status), status)
        with self.assertRaises(StandardError):
            Job.checkStatus(status.lower())
        with self.assertRaises(StandardError):
            Job.checkStatus("INVALID_STATUS")

    def test_updateStatus(self):
        job = Job(self.uid, self.name, self.status, self.createtime, self.submittime, self.sparkjob)
        self.assertEqual(job.status, self.status)
        job.updateStatus(FINISHED)
        self.assertEqual(job.status, FINISHED)
        # check update of a wrong status
        with self.assertRaises(StandardError):
            job.updateStatus("WRONG_STATUS")

    def test_convertToDict(self):
        job = Job(self.uid, self.name, self.status, self.createtime, self.submittime, self.sparkjob)
        obj = job.dict()
        self.assertEqual(obj["uid"], self.uid)
        self.assertEqual(obj["status"], self.status)
        self.assertEqual(obj["createtime"], self.createtime)
        self.assertEqual(obj["submittime"], self.submittime)
        self.assertEqual(obj["sparkjob"], self.sparkjob)
        self.assertEqual(obj["priority"], self.submittime)
        self.assertEqual(obj["starttime"], TIME_NONE)
        self.assertEqual(obj["finishtime"], TIME_NONE)
        # change priority of a job
        job.updatePriority(99)
        obj = job.dict()
        self.assertEqual(obj["priority"], 99)
        # change start and finish times
        newTime = utils.currentTimeMillis()
        job.updateStartTime(newTime)
        job.updateFinishTime(newTime)
        obj = job.dict()
        self.assertEqual(obj["starttime"], newTime)
        self.assertEqual(obj["finishtime"], newTime)

    def test_convertFromDict(self):
        job = Job(self.uid, self.name, self.status, self.createtime, self.submittime,
            self.sparkjob, priority=1)
        obj = job.dict()
        copy = Job.fromDict(obj)
        self.assertEqual(copy.uid, self.uid)
        self.assertEqual(copy.status, self.status)
        self.assertEqual(copy.createtime, self.createtime)
        self.assertEqual(copy.submittime, self.submittime)
        self.assertEqual(copy.sparkjob, self.sparkjob)
        self.assertEqual(copy.priority, job.priority)
        self.assertEqual(copy.starttime, TIME_NONE)
        self.assertEqual(copy.finishtime, TIME_NONE)
        # finish job check finish time again
        newTime = utils.currentTimeMillis()
        job.updateStartTime(newTime)
        job.updateFinishTime(newTime)
        copy = Job.fromDict(job.dict())
        self.assertEqual(copy.starttime, newTime)
        self.assertEqual(copy.finishtime, newTime)

    def test_updateSparkAppId(self):
        job = Job(self.uid, self.name, self.status, self.createtime, self.submittime, self.sparkjob)
        self.assertEqual(job.sparkAppId, None)
        obj = job.dict()
        self.assertEqual(obj["sparkappid"], None)
        self.assertEqual(Job.fromDict(obj).sparkAppId, None)
        # update status and check that is updated everywhere
        sparkAppId = "spark_app12345"
        job.updateSparkAppId(sparkAppId)
        self.assertEqual(job.sparkAppId, sparkAppId)
        obj = job.dict()
        self.assertEqual(obj["sparkappid"], sparkAppId)
        self.assertEqual(Job.fromDict(obj).sparkAppId, sparkAppId)

    def test_updateFinishTime(self):
        job = Job(self.uid, self.name, self.status, self.createtime, self.submittime, self.sparkjob)
        self.assertEqual(job.finishtime, TIME_NONE)
        job.updateFinishTime(TIME_UNKNOWN)
        self.assertEqual(job.finishtime, TIME_UNKNOWN)
        now = utils.currentTimeMillis()
        job.updateFinishTime(now)
        self.assertEqual(job.finishtime, now)
        # check out of range time
        job.updateFinishTime(-1000L)
        self.assertEqual(job.finishtime, TIME_UNKNOWN)

    def test_updateStartTime(self):
        job = Job(self.uid, self.name, self.status, self.createtime, self.submittime, self.sparkjob)
        self.assertEqual(job.starttime, TIME_NONE)
        job.updateStartTime(TIME_UNKNOWN)
        self.assertEqual(job.starttime, TIME_UNKNOWN)
        now = utils.currentTimeMillis()
        job.updateStartTime(now)
        self.assertEqual(job.starttime, now)
        # check out of range time
        job.updateStartTime(-1000L)
        self.assertEqual(job.starttime, TIME_UNKNOWN)

# Load test suites
def _suites():
    return [
        JobTestSuite
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
