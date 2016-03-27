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
from octohaven import db, api
from cron import CronExpression

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
    def create(cls, **opts):
        if "name" not in opts:
            raise StandardError("Expected 'name' key in %s" % json.dumps(opts))
        if "cron" not in opts:
            raise StandardError("Expected 'cron' key in %s" % json.dumps(opts))
        if "job_uid" not in opts:
            raise StandardError("Expected 'job_uid' key in %s" % json.dumps(opts))
        timetable = Timetable(name=opts["name"], status=cls.ACTIVE,
            createtime=utils.currentTimeMillis(), canceltime=None, cron=opts["cron"],
            job_uid=opts["job_uid"])
        db.session.add(timetable)
        db.session.commit()
        return timetable

    @classmethod
    @utils.sql
    def get(cls, uid):
        return cls.query.get(uid)

    @classmethod
    @utils.sql
    def list(cls, status):
        filtered = cls.query.filter_by(status = status) if status in cls.STATUSES else cls.query
        return filtered.order_by(desc(cls.createtime)).all()

    @classmethod
    @utils.sql
    def pause(cls, timetable):
        if not timetable.canPause():
            raise StandardError("Cannot pause timetable")
        timetable.status = cls.PAUSED
        db.session.commit()

    @classmethod
    @utils.sql
    def resume(cls, timetable):
        if not timetable.canResume():
            raise StandardError("Cannot resume timetable")
        timetable.status = cls.ACTIVE
        db.session.commit()

    @classmethod
    @utils.sql
    def cancel(cls, timetable):
        if not timetable.canCancel():
            raise StandardError("Cannot cancel timetable")
        timetable.status = cls.CANCELLED
        timetable.setCanceltime(utils.currentTimeMillis())
        db.session.commit()

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

    def __init__(self, timetable_uid, job_uid, createtime):
        self.timetable_uid = timetable_uid
        self.job_uid = job_uid
        self.createtime = createtime

    @classmethod
    @utils.sql
    def create(cls, **opts):
        if "timetable_uid" not in opts:
            raise StandardError("Expected 'timetable_uid' key in %s" % json.dumps(opts))
        if "job_uid" not in opts:
            raise StandardError("Expected 'job_uid' key in %s" % json.dumps(opts))
        # We always insert current timestamp, it cannot be overwritten
        stats = TimetableStats(timetable_uid=opts["timetable_uid"], job_uid=opts["job_uid"],
            createtime=utils.currentTimeMillis())
        db.session.add(stats)
        db.session.commit()
        return stats

    def json(self):
        return {
            "timetable_uid": self.timetable_uid,
            "job_uid": self.job_uid,
            "createtime": self.createtime
        }
