#!/usr/bin/env python

import unittest, json, time
import src.utils as utils
from types import DictType
from src.octohaven import db
from src.job import Job
from src.timetable import Timetable, TimetableStats

class TimetableTestSuite(unittest.TestCase):
    def setUp(self):
        TimetableStats.query.delete()
        Timetable.query.delete()
        Job.query.delete()

        self.opts = {
            "name": "test-name",
            "status": Timetable.ACTIVE,
            "createtime": 1L,
            "canceltime": None,
            "cron": "* * * * * *",
            "job_uid": 1
        }
        self.jobOpts = {
            "name": "test-job",
            "status": Job.READY,
            "priority": 1L,
            "createtime": 1L,
            "submittime": 1L,
            "entrypoint": "com.test.Main",
            "jar": "/tmp/file.jar",
            "dmemory": "4g",
            "ememory": "4g",
            "options": {},
            "jobconf": []
        }

    def tearDown(self):
        pass

    def test_create(self):
        timetable = Timetable(**self.opts)
        self.assertEquals(timetable.name, self.opts["name"])
        self.assertEquals(timetable.status, self.opts["status"])
        self.assertEquals(timetable.createtime, self.opts["createtime"])
        self.assertEquals(timetable.canceltime, self.opts["canceltime"])
        self.assertEquals(timetable.cron, self.opts["cron"])
        self.assertEquals(timetable.job_uid, self.opts["job_uid"])

    def test_create1(self):
        with self.assertRaises(StandardError):
            self.opts["status"] = None
            Timetable(**self.opts)

    def test_create2(self):
        with self.assertRaises(StandardError):
            self.opts["createtime"] = -1L
            Timetable(**self.opts)
        with self.assertRaises(StandardError):
            del self.opts["createtime"]
            Timetable(**self.opts)

    def test_create3(self):
        with self.assertRaises(StandardError):
            self.opts["cron"] = ""
            Timetable(**self.opts)

    def test_canPause(self):
        timetable = Timetable(**self.opts)
        self.assertEquals(timetable.canPause(), True)
        self.assertEquals(timetable.canResume(), False)
        self.assertEquals(timetable.canCancel(), True)

    def test_canResume(self):
        timetable = Timetable(**self.opts)
        timetable.status = Timetable.PAUSED
        self.assertEquals(timetable.canPause(), False)
        self.assertEquals(timetable.canResume(), True)
        self.assertEquals(timetable.canCancel(), True)

    def test_canCancel(self):
        timetable = Timetable(**self.opts)
        timetable.status = Timetable.CANCELLED
        self.assertEquals(timetable.canPause(), False)
        self.assertEquals(timetable.canResume(), False)
        self.assertEquals(timetable.canCancel(), False)

    def test_add(self):
        with self.assertRaises(StandardError):
            Timetable.create(db.session, **{})
        with self.assertRaises(StandardError):
            Timetable.create(db.session, **{"name": "test"})
        with self.assertRaises(StandardError):
            Timetable.create(db.session, **{"name": "test", "cron": "* * * * * *"})
        # test correct input, though it has more keys than required
        # should fail since there is no such job exists
        job = Job.create(db.session, **self.jobOpts)
        self.opts["job_uid"] = job.uid
        timetable = Timetable.create(db.session, **self.opts)
        self.assertTrue(timetable.createtime > utils.currentTimeMillis() - 5000)
        self.assertEquals(timetable.job.json(), job.json())

    def test_get(self):
        job = Job.create(db.session, **self.jobOpts)
        self.opts["job_uid"] = job.uid
        timetable = Timetable.create(db.session, **self.opts)
        res = Timetable.get(db.session, timetable.uid)
        self.assertEquals(res.json(), timetable.json())
        # test non-existent key
        res = Timetable.get(db.session, "")
        self.assertEquals(res, None)

    def test_list(self):
        job = Job.create(db.session, **self.jobOpts)
        self.opts["job_uid"] = job.uid
        for x in range(5):
            Timetable.create(db.session, **self.opts)
        arr = Timetable.list(db.session, None)
        self.assertEquals(len(arr), 5)

    def test_pause(self):
        job = Job.create(db.session, **self.jobOpts)
        self.opts["job_uid"] = job.uid
        timetable = Timetable.create(db.session, **self.opts)
        Timetable.pause(db.session, timetable)
        timetable.status = Timetable.PAUSED
        # try pausing already paused timetable
        with self.assertRaises(StandardError):
            Timetable.pause(db.session, timetable)

    def test_resume(self):
        job = Job.create(db.session, **self.jobOpts)
        self.opts["job_uid"] = job.uid
        timetable = Timetable.create(db.session, **self.opts)
        timetable.status = Timetable.PAUSED
        Timetable.resume(db.session, timetable)
        timetable.status = Timetable.ACTIVE
        # try resuming already active timetable
        with self.assertRaises(StandardError):
              Timetable.resume(db.session, timetable)

    def test_cancel(self):
        job = Job.create(db.session, **self.jobOpts)
        self.opts["job_uid"] = job.uid
        timetable = Timetable.create(db.session, **self.opts)
        Timetable.cancel(db.session, timetable)
        timetable.status = Timetable.CANCELLED
        # try cancelling already cancelled timetable
        with self.assertRaises(StandardError):
            Timetable.cancel(db.session, timetable)

    def test_json(self):
        job = Job.create(db.session, **self.jobOpts)
        self.opts["job_uid"] = job.uid
        timetable = Timetable.create(db.session, **self.opts)
        res = Timetable.get(db.session, timetable.uid).json()
        self.assertEquals(res["name"], timetable.name)
        self.assertEquals(res["status"], timetable.status)
        self.assertEquals(res["createtime"], timetable.createtime)
        self.assertEquals(res["canceltime"], timetable.canceltime)
        self.assertEquals(res["cron"], timetable.cronExpression().json())
        self.assertEquals(res["job"], timetable.job.json())

    # Test manual appending of statistics
    def test_stats(self):
        job = Job.create(db.session, **self.jobOpts)
        self.opts["job_uid"] = job.uid
        timetable = Timetable.create(db.session, **self.opts)

        latestStats = None
        for x in range(10):
            spawnedJob = Job.create(db.session, **self.jobOpts)
            latestStats = TimetableStats(timetable_uid=timetable.uid, job_uid=spawnedJob.uid,
                createtime=x)
            db.session.add(latestStats)
            db.session.commit()
        # retrieve stats and compare with iterator
        stats = timetable.json()["stats"]
        self.assertEquals(stats["jobs"], 10)
        self.assertEquals(stats["last_time"], latestStats.createtime)
        self.assertEquals(stats["last_job_uid"], latestStats.job_uid)

    # Test auto appending of statistics
    def test_registerNewJob(self):
        job = Job.create(db.session, **self.jobOpts)
        self.opts["job_uid"] = job.uid
        timetable = Timetable.create(db.session, **self.opts)

        spawnedJob = None
        for x in range(7):
            spawnedJob = Timetable.registerNewJob(db.session, timetable)
            time.sleep(0.05)
        # retrieve stats and compare with iterator
        stats = timetable.json()["stats"]
        self.assertEquals(stats["jobs"], 7)
        self.assertEquals(stats["last_job_uid"], spawnedJob.uid)

# Load test suites
def _suites():
    return [
        TimetableTestSuite
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
