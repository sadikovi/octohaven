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

import utils
from flask import json
from sqlalchemy import desc
from types import LongType
from octohaven import db, api, ee
from cron import CronExpression
from job import Job

class Timetable(db.Model):
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    createtime = db.Column(db.BigInteger, nullable=False)
    canceltime = db.Column(db.BigInteger)
    cron = db.Column(db.String(255), nullable=False)
    job_uid = db.Column(db.Integer, db.ForeignKey("job.uid"))
    # Backref property for timetable
    job = db.relationship("Job", backref=db.backref("timetable", lazy="joined"), uselist=False)
    # Backref property for timetable statistics
    stats = db.relationship("TimetableStats", lazy="dynamic")
    # List of statuses available
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"
    STATUSES = [ACTIVE, PAUSED, CANCELLED]

    def __init__(self, name, status, createtime, canceltime, cron, job_uid):
        self.name = utils.getCanonicalName(name)
        if status not in self.STATUSES:
            raise StandardError("Unrecognized status '%s'" % status)
        self.status = status
        # check that createtime is valid timestamp
        utils.assertInstance(createtime, LongType)
        if not createtime > 0:
            raise StandardError("Create time must be > 0, got %s" % createtime)
        self.createtime = createtime
        # canceltime can be None
        self.canceltime = canceltime
        self.cron = CronExpression.fromPattern(str(cron).strip()).pattern
        self.job_uid = job_uid

    def cronExpression(self):
        return CronExpression.fromPattern(self.cron)

    def setCanceltime(self, canceltime):
        self.canceltime = canceltime

    def canPause(self):
        return self.status == self.ACTIVE

    def canResume(self):
        return self.status == self.PAUSED

    def canCancel(self):
        return self.status != self.CANCELLED

    @classmethod
    @utils.sql
    def create(cls, session, **opts):
        if "name" not in opts:
            raise StandardError("Expected 'name' key in %s" % json.dumps(opts))
        if "cron" not in opts:
            raise StandardError("Expected 'cron' key in %s" % json.dumps(opts))
        if "job_uid" not in opts:
            raise StandardError("Expected 'job_uid' key in %s" % json.dumps(opts))
        timetable = Timetable(name=opts["name"], status=cls.ACTIVE,
            createtime=utils.currentTimeMillis(), canceltime=None, cron=opts["cron"],
            job_uid=opts["job_uid"])
        session.add(timetable)
        session.commit()
        ee.emit("timetable-created", timetable.uid)
        return timetable

    @classmethod
    @utils.sql
    def get(cls, session, uid):
        return session.query(cls).get(uid)

    @classmethod
    @utils.sql
    def list(cls, session, status=None):
        query = session.query(cls)
        if status in cls.STATUSES:
            query = query.filter_by(status = status)
        return query.order_by(desc(cls.createtime)).all()

    # Method retrieves all non-cancelled timetables that we need to scheduling
    @classmethod
    @utils.sql
    def listEnabled(cls, session):
        filtered = session.query(cls).filter(cls.status != cls.CANCELLED)
        return filtered.all()

    @classmethod
    @utils.sql
    def pause(cls, session, timetable):
        if not timetable.canPause():
            raise StandardError("Cannot pause timetable")
        timetable.status = cls.PAUSED
        session.commit()

    @classmethod
    @utils.sql
    def resume(cls, session, timetable):
        if not timetable.canResume():
            raise StandardError("Cannot resume timetable")
        timetable.status = cls.ACTIVE
        session.commit()

    @classmethod
    @utils.sql
    def cancel(cls, session, timetable):
        if not timetable.canCancel():
            raise StandardError("Cannot cancel timetable")
        timetable.status = cls.CANCELLED
        timetable.setCanceltime(utils.currentTimeMillis())
        session.commit()
        ee.emit("timetable-cancelled", timetable.uid)

    # Method returns fresh copy of job with zero delay, because we are launching it using timetable
    # Another note is that we are changing job name to reflect periodic nature and timetable launch
    @classmethod
    @utils.sql
    def jobCopy(cls, timetable):
        now = utils.currentTimeMillis()
        # create dummy job, we overwrite some parameters later
        deepCopy = timetable.job.jobCopy(name="%s-T-%s" % (timetable.name, now), status=Job.READY,
            priority=now, createtime=now, submittime=now)
        return deepCopy

    @classmethod
    @utils.sql
    def registerNewJob(cls, session, timetable):
        session.begin(subtransactions=True)
        copiedJob = cls.jobCopy(timetable)
        session.add(copiedJob)
        session.commit()
        # add statistics after saving job
        session.begin(subtransactions=True)
        stats = TimetableStats(timetable.uid, copiedJob.uid, copiedJob.createtime)
        session.add(stats)
        session.commit()
        return copiedJob

    def json(self):
        # Construct statistics
        numJobs = self.stats.count()
        lastStats = self.stats.order_by(desc(TimetableStats.createtime)).first()

        return {
            "uid": self.uid,
            "name": self.name,
            "status": self.status,
            "createtime": self.createtime,
            "canceltime": self.canceltime,
            "job": self.job.json() if self.job else None,
            "cron": self.cronExpression().json(),
            "stats": {
                "jobs": numJobs,
                "last_time": lastStats.createtime if lastStats else None,
                "last_job_uid": lastStats.job_uid if lastStats else None,
                "last_job_html_url": ("/job/%s" % lastStats.job_uid) if lastStats else None
            },
            "html_url": "/timetable/%s" % self.uid,
            "url": api("/timetable/get/%s" % self.uid),
            "resume_url": api("/timetable/resume/%s" % self.uid) if self.canResume() else None,
            "pause_url": api("/timetable/pause/%s" % self.uid) if self.canPause() else None,
            "cancel_url": api("/timetable/cancel/%s" % self.uid) if self.canCancel() else None
        }

class TimetableStats(db.Model):
    index = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timetable_uid = db.Column(db.Integer, db.ForeignKey("timetable.uid"))
    job_uid = db.Column(db.Integer, db.ForeignKey("job.uid"))
    createtime = db.Column(db.BigInteger, nullable=False)

    def __init__(self, timetable_uid, job_uid, createtime=utils.currentTimeMillis()):
        self.timetable_uid = timetable_uid
        self.job_uid = job_uid
        self.createtime = createtime

    def json(self):
        return {
            "timetable_uid": self.timetable_uid,
            "job_uid": self.job_uid,
            "createtime": self.createtime
        }
