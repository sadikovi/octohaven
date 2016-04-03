#!/usr/bin/env python

#
# Copyright 2015 sadikovi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import unittest, json
import src.utils as utils
from types import DictType
from src.sparkmodule import SPARK_OCTOHAVEN_JOB_ID
from src.octohaven import db, sparkContext
from src.job import Job
from src.timetable import Timetable, TimetableStats

class JobTestSuite(unittest.TestCase):
    def setUp(self):
        TimetableStats.query.delete()
        Timetable.query.delete()
        Job.query.delete()
        db.session.commit()

        self.opts = {
            "name": "test-job",
            "status": Job.READY,
            "priority": 1L,
            "createtime": 1L,
            "submittime": 1L,
            "entrypoint": "com.test.Main",
            "jar": "/tmp/file.jar",
            "dmemory": "4g",
            "ememory": "4g",
            "options": {
                "spark.driver.memory": "8g",
                "spark.executor.memory": "8g",
                "spark.shuffle.spill": "true",
                "spark.file.overwrite": "true"
            },
            "jobconf": ["a", "b", "c"]
        }

    def tearDown(self):
        TimetableStats.query.delete()
        Timetable.query.delete()
        Job.query.delete()
        db.session.commit()

    def test_create(self):
        job = Job(**self.opts)
        self.assertEquals(job.name, self.opts["name"])
        self.assertEquals(job.status, self.opts["status"])
        self.assertEquals(job.createtime, self.opts["createtime"])
        self.assertEquals(job.submittime, self.opts["submittime"])
        self.assertEquals(job.entrypoint, self.opts["entrypoint"])
        self.assertEquals(job.jar, self.opts["jar"])
        self.opts["spark.driver.memory"] = self.opts["dmemory"]
        self.opts["spark.executor.memory"] = self.opts["ememory"]
        self.assertEquals(job.getSparkOptions(), self.opts["options"])
        self.assertEquals(job.getJobConf(), self.opts["jobconf"])

    def test_create1(self):
        with self.assertRaises(StandardError):
            del self.opts["createtime"]
            Job(**self.opts)
        with self.assertRaises(StandardError):
            self.opts["createtime"] = 1L
            del self.opts["submittime"]
            Job(**self.opts)
        with self.assertRaises(StandardError):
            self.opts["createtime"] = -1L
            self.opts["submittime"] = -1L
            Job(**self.opts)

    def test_create2(self):
        with self.assertRaises(StandardError):
            self.opts["priority"] = None
            Job(**self.opts)

    def test_create3(self):
        with self.assertRaises(StandardError):
            self.opts["entrypoint"] = ""
            Job(**self.opts)
        with self.assertRaises(StandardError):
            del self.opts["entrypoint"]
            Job(**self.opts)

    def test_create4(self):
        with self.assertRaises(StandardError):
            self.opts["jar"] = ""
            Job(**self.opts)
        with self.assertRaises(StandardError):
            self.opts["jar"] = "/tmp/file.txt"
            Job(**self.opts)
        with self.assertRaises(StandardError):
            del self.opts["jar"]
            Job(**self.opts)

    def test_create5(self):
        self.opts["options"] = {}
        self.opts["jobconf"] = []
        job = Job(**self.opts)
        self.assertEquals(job.getSparkOptions(), {"spark.driver.memory": self.opts["dmemory"],
            "spark.executor.memory": self.opts["ememory"]})
        self.assertEquals(job.getJobConf(), [])

    def test_getSparkOptions(self):
        job = Job(**self.opts)
        self.opts["spark.driver.memory"] = self.opts["dmemory"]
        self.opts["spark.executor.memory"] = self.opts["ememory"]
        self.assertEquals(job.getSparkOptions(), self.opts["options"])

    def test_getJobConf(self):
        job = Job(**self.opts)
        self.assertEquals(job.getJobConf(), self.opts["jobconf"])

    def test_canClose(self):
        job = Job(**self.opts)
        self.assertEquals(job.canClose(), True)
        for status in [Job.CLOSED, Job.RUNNING, Job.FINISHED]:
            job.status = status
            self.assertEquals(job.canClose(), False)

    def test_add(self):
        job = Job.create(db.session, **self.opts)
        arr = Job.list(db.session, None)
        self.assertTrue(len(arr), 1)

    def test_add1(self):
        self.opts["delay"] = 2000
        job = Job.create(db.session, **self.opts)
        self.assertEquals(job.submittime, job.createtime + 2000 * 1000)
        # negative delay equals to 0 seconds
        self.opts["delay"] = -2000
        job = Job.create(db.session, **self.opts)
        self.assertEquals(job.submittime, job.createtime)

    def test_get(self):
        job = Job.create(db.session, **self.opts)
        res = Job.get(db.session, job.uid)
        self.assertEquals(res.json(), job.json())
        # fetch job with non-existent job id
        res = Job.get(db.session, "")
        self.assertEquals(res, None)

    def test_list(self):
        i = 0L
        for x in range(10):
            Job.create(db.session, **self.opts)
        arr = Job.list(db.session, None)
        self.assertEquals(len(arr), 10)
        times = [x.createtime for x in arr]
        self.assertEquals(times, sorted(times, reverse=True))
        # test selecting status
        arr = Job.list(db.session, Job.READY, limit=1)
        self.assertEquals(len(arr), 1)
        arr = Job.list(db.session, Job.READY, limit=5)
        self.assertEquals(len(arr), 5)
        arr = Job.list(db.session, Job.READY, limit=0)
        self.assertEquals(len(arr), 10)
        arr = Job.list(db.session, Job.READY, limit=-1)
        self.assertEquals(len(arr), 10)

    def test_close(self):
        job = Job.create(db.session, **self.opts)
        self.assertEquals(job.status, Job.READY)
        Job.close(db.session, job)
        self.assertEquals(job.status, Job.CLOSED)
        # try closing already closed job
        with self.assertRaises(StandardError):
            Job.close(db.session, job)
        with self.assertRaises(StandardError):
            job.status = Job.RUNNING
            Job.close(db.session, job)
        with self.assertRaises(StandardError):
            job.status = Job.FINISHED
            Job.close(db.session, job)

    def test_run(self):
        job = Job.create(db.session, **self.opts)
        Job.run(db.session, job)
        self.assertEqual(job.status, Job.RUNNING)
        # check that start time is close to current time
        self.assertTrue(job.starttime > utils.currentTimeMillis() - 2000)
        # should fail to run already running job
        with self.assertRaises(StandardError):
            Job.run(db.session, job)

    def test_finish(self):
        job = Job.create(db.session, **self.opts)
        # should not be able to finish not running job
        with self.assertRaises(StandardError):
            Job.finish(db.session, job)
        # Launch job and finish it
        Job.run(db.session, job)
        Job.finish(db.session, job)
        self.assertEqual(job.status, Job.FINISHED)
        self.assertTrue(job.finishtime > utils.currentTimeMillis() - 2000)
        # should fail to finish already finished job
        with self.assertRaises(StandardError):
            Job.finish(db.session, job)

    def test_json(self):
        job = Job.create(db.session, **self.opts)
        obj = job.json()
        self.assertEquals(obj["name"], job.name)
        self.assertEquals(obj["status"], job.status)
        self.assertEquals(obj["createtime"], job.createtime)
        self.assertEquals(obj["submittime"], job.submittime)
        self.assertEquals(obj["entrypoint"], job.entrypoint)
        self.assertEquals(obj["jar"], job.jar)
        self.assertEquals(obj["options"], job.getSparkOptions())
        self.assertEquals(obj["jobconf"], job.getJobConf())

    def test_jobCopy(self):
        job = Job.create(db.session, **self.opts)
        copy = job.jobCopy(name="a", status=Job.READY, priority=1, createtime=2L, submittime=2L)
        self.assertEquals(copy.uid, None)
        self.assertEquals(copy.name, "a")
        self.assertEquals(copy.status, Job.READY)
        self.assertEquals(copy.priority, 1)
        self.assertEquals(copy.createtime, 2L)
        self.assertEquals(copy.submittime, 2L)
        self.assertEquals(copy.sparkappid, None)
        self.assertEquals(copy.starttime, None)
        self.assertEquals(copy.finishtime, None)
        # these properties should be the same
        self.assertEquals(copy.options, job.options)
        self.assertEquals(copy.jobconf, job.jobconf)
        self.assertEquals(copy.entrypoint, job.entrypoint)
        self.assertEquals(copy.jar, job.jar)

    def test_jobCopy1(self):
        self.opts["status"] = Job.DELAYED
        self.opts["submittime"] = 100L
        self.opts["sparkappid"] = "1-2-3"
        self.opts["starttime"] = 101L
        self.opts["finishtime"] = 110L
        job = Job.create(db.session, **self.opts)
        copy = job.jobCopy(name="a", status=Job.READY, priority=1, createtime=2L, submittime=2L)
        self.assertEquals(copy.uid, None)
        self.assertEquals(copy.name, "a")
        self.assertEquals(copy.status, Job.READY)
        self.assertEquals(copy.priority, 1)
        self.assertEquals(copy.createtime, 2L)
        self.assertEquals(copy.submittime, 2L)
        self.assertEquals(copy.sparkappid, None)
        self.assertEquals(copy.starttime, None)
        self.assertEquals(copy.finishtime, None)
        # these properties should be the same
        self.assertEquals(copy.options, job.options)
        self.assertEquals(copy.jobconf, job.jobconf)
        self.assertEquals(copy.entrypoint, job.entrypoint)
        self.assertEquals(copy.jar, job.jar)

    def test_execCommand(self):
        job = Job.create(db.session, **self.opts)
        cmd = job.execCommand(sparkContext)
        self.assertEqual(sorted(cmd), sorted(["spark-submit", "--name", "test-job", "--master",
            "spark://sandbox:7077", "--conf", "%s=%s" % (SPARK_OCTOHAVEN_JOB_ID, job.uid),
            "--conf", "spark.executor.memory=4g", "--conf", "spark.driver.memory=4g",
            "--conf", "spark.file.overwrite=true", "--conf", "spark.shuffle.spill=true",
            "--class", "com.test.Main", "/tmp/file.jar", "a", "b", "c"]))

    def test_execCommandWithExtraOptions(self):
        job = Job.create(db.session, **self.opts)
        cmd = job.execCommand(sparkContext, ["foo=bar"], {"spark.sql.shuffle.partitions": 200})
        self.assertEqual(sorted(cmd), sorted(["spark-submit", "--name", "test-job", "--master",
            "spark://sandbox:7077", "--conf", "%s=%s" % (SPARK_OCTOHAVEN_JOB_ID, job.uid),
            "--conf", "spark.executor.memory=4g", "--conf", "spark.driver.memory=4g",
            "--conf", "spark.file.overwrite=true", "--conf", "spark.shuffle.spill=true",
            "--conf", "spark.sql.shuffle.partitions=200", "--class", "com.test.Main",
            "/tmp/file.jar", "a", "b", "c", "foo=bar"]))

    def test_execCommandOrder(self):
        job = Job.create(db.session, **self.opts)
        cmd = job.execCommand(sparkContext, ["foo=bar"], {"spark.sql.shuffle.partitions": 200})
        anon = [x for x in cmd if x.startswith("--") or x == "spark-submit" or x.endswith(".jar")]
        self.assertEqual(anon, ["spark-submit", "--name", "--master", "--conf", "--conf", "--conf",
            "--conf", "--conf", "--conf", "--class", "/tmp/file.jar"])
        self.assertEqual(len(cmd), 24)
        self.assertEqual(cmd[20:], ["a", "b", "c", "foo=bar"])

    def test_listRunning(self):
        arr = [("ready", Job.READY), ("running", Job.RUNNING), ("finished", Job.FINISHED),
            ("running", Job.RUNNING)]
        for name, status in arr:
            job = Job.create(db.session, **self.opts)
            job.name = name
            job.status = status
            db.session.commit()
        jobs = Job.listRunning(db.session)
        self.assertEqual(len(jobs), 2)
        self.assertEqual([x.status for x in jobs], [Job.RUNNING, Job.RUNNING])

    def test_listRunnable(self):
        arr = [("ready", Job.READY), ("running", Job.RUNNING), ("finished", Job.FINISHED),
            ("running", Job.RUNNING), ("delayed", Job.DELAYED)]
        for name, status in arr:
            job = Job.create(db.session, **self.opts)
            job.name = name
            job.status = status
            if status is Job.DELAYED:
                job.submittime = job.submittime - 10000
                job.priority = job.submittime / 1000L
            db.session.commit()
        jobs = Job.listRunnable(db.session, 5, utils.currentTimeMillis())
        self.assertEqual(len(jobs), 2)
        self.assertEqual([x.name for x in jobs], ["delayed", "ready"])
        self.assertEqual([x.status for x in jobs], [Job.DELAYED, Job.READY])

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
