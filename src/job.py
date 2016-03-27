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

import utils, shlex
from flask import json
from sqlalchemy import desc
from types import LongType, DictType, ListType
from octohaven import db, api

class Job(db.Model):
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    createtime = db.Column(db.BigInteger, nullable=False)
    submittime = db.Column(db.BigInteger, nullable=False)
    starttime = db.Column(db.BigInteger)
    finishtime = db.Column(db.BigInteger)
    priority = db.Column(db.BigInteger, nullable=False)
    # Spark job options
    sparkappid = db.Column(db.String(255))
    entrypoint = db.Column(db.String(1024), nullable=False)
    jar = db.Column(db.String(1024), nullable=False)
    options = db.Column(db.String(2000), nullable=False)
    jobconf = db.Column(db.String(2000), nullable=False)
    # List of statuses available
    READY = "READY"
    DELAYED = "DELAYED"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    CLOSED = "CLOSED"
    STATUSES = [READY, DELAYED, RUNNING, FINISHED, CLOSED]

    def __init__(self, name, status, priority, createtime, submittime, entrypoint, jar, dmemory,
        ememory, options, jobconf):
        # canonicalize name
        self.name = utils.getCanonicalName(name)

        # make sure that timestamps are longs
        utils.assertInstance(createtime, LongType)
        if not createtime > 0:
            raise StandardError("Create time must be > 0, got %s" % createtime)
        self.createtime = createtime
        utils.assertInstance(submittime, LongType)
        if not submittime > 0:
            raise StandardError("Create time must be > 0, got %s" % submittime)
        self.submittime = submittime

        # check status
        if status not in self.STATUSES:
            raise StandardError("Unrecognized status '%s'" % status)
        self.status = status
        # validate priority for the job
        self.priority = utils.validatePriority(priority)

        # parse Spark options into key-value pairs
        parsedOptions = options if isinstance(options, DictType) else {}
        if not parsedOptions:
            cli = filter(lambda x: len(x) == 2, [x.split("=", 1) for x in shlex.split(str(options))])
            for pre in cli:
                parsedOptions[pre[0]] = pre[1]
        # manually set driver or executor memory takes precedence over Spark options
        parsedOptions["spark.driver.memory"] = utils.validateMemory(dmemory)
        parsedOptions["spark.executor.memory"] = utils.validateMemory(ememory)
        # for storing in database options must be a string
        self.options = json.dumps(parsedOptions)

        # parse job configuration/options into list of values
        parsedJobConf = jobconf if isinstance(jobconf, ListType) else shlex.split(str(jobconf))
        self.jobconf = json.dumps(parsedJobConf)

        # entrypoint for the Spark job
        self.entrypoint = utils.validateEntrypoint(entrypoint)
        # jar file path
        self.jar = utils.validateJarPath(jar)

    def setAppId(self, appId):
        self.sparkappid = appId

    def setStarttime(self, starttime):
        utils.assertInstance(starttime, LongType)
        self.starttime = starttime

    def setFinishtime(self, finishtime):
        utils.assertInstance(finishtime, LongType)
        self.finishtime = finishtime

    # Return Spark options as dictionary
    def getSparkOptions(self):
        return json.loads(self.options)

    # Return Job configuration/options as dictionary
    def getJobConf(self):
        return json.loads(self.jobconf)

    def canClose(self):
        return self.status == self.READY or self.status == self.DELAYED

    @classmethod
    @utils.sql
    def create(cls, **opts):
        # Resolve primary options
        createtime = utils.currentTimeMillis()
        # Resolve delay in seconds, if delay is negative it is reset to 0
        delay = utils.intOrElse(opts["delay"] if "delay" in opts else 0, 0)
        resolvedDelay = 0 if delay < 0 else delay
        # Resolve status based on delay
        status = cls.READY if resolvedDelay == 0 else cls.DELAYED
        # Resolve submit time (when job will be added to the queue)
        submittime = createtime + resolvedDelay * 1000
        # Resolve status based on submittime (if submit time more than 1 second greater than create
        # time, we mark it as delayed, otherwise it is ready
        status = cls.DELAYED if submittime > createtime + 1000 else cls.READY
        # Resolve priority, if status is READY then priority is submittime else truncated
        # submittime, so delayed job can be scheduled as soon as possible once it is queued
        priority = submittime if status == cls.READY else submittime / 1000L
        # Create (including validation and options parsing) Job instance
        job = cls(name=opts["name"], status=status, priority=priority,
            createtime=createtime, submittime=submittime,
            entrypoint=opts["entrypoint"], jar=opts["jar"],
            dmemory=opts["dmemory"], ememory=opts["ememory"],
            options=opts["options"], jobconf=opts["jobconf"])
        db.session.add(job)
        db.session.commit()
        return job

    @classmethod
    @utils.sql
    def get(cls, uid):
        return cls.query.get(uid)

    @classmethod
    @utils.sql
    def list(cls, status, limit=100):
        filtered = cls.query.filter_by(status = status) if status in cls.STATUSES else cls.query
        limit = limit if limit > 0 else 1
        return filtered.order_by(desc(cls.createtime)).limit(limit).all()

    @classmethod
    @utils.sql
    def close(cls, job):
        if not job.canClose():
            raise StandardError("Cannot close job")
        job.status = cls.CLOSED
        db.session.commit()

    def json(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "status": self.status,
            "createtime": self.createtime,
            "submittime": self.submittime,
            "starttime": self.starttime,
            "finishtime": self.finishtime,
            "priority": self.priority,
            "sparkappid": self.sparkappid,
            "entrypoint": self.entrypoint,
            "jar": self.jar,
            "options": self.getSparkOptions(),
            "jobconf": self.getJobConf(),
            "html_url": "/job/%s" % self.uid,
            "create_timetable_html_url": "/create/timetable/job/%s" % self.uid,
            "url": api("/job/get/%s" % self.uid),
            "close_url": api("/job/close/%s" % self.uid) if self.canClose() else None
        }
