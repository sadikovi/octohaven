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
        # Canonicalize name
        self.name = utils.getCanonicalName(name)
        # Make sure that timestamps are longs
        utils.assertInstance(createtime, LongType)
        if not createtime > 0:
            raise StandardError("Create time must be > 0, got %s" % createtime)
        self.createtime = createtime
        utils.assertInstance(submittime, LongType)
        if not submittime > 0:
            raise StandardError("Create time must be > 0, got %s" % submittime)
        self.submittime = submittime

        # Check status
        if status not in self.STATUSES:
            raise StandardError("Unrecognized status '%s'" % status)
        self.status = status
        # Validate priority for the job
        self.priority = utils.validatePriority(priority)

        # Parse Spark options into key-value pairs
        parsedOptions = options if isinstance(options, DictType) else {}
        if not parsedOptions:
            cli = filter(lambda x: len(x) == 2, [x.split("=", 1) for x in shlex.split(str(options))])
            for pre in cli:
                parsedOptions[pre[0]] = pre[1]
        # Manually set driver or executor memory takes precedence over Spark options
        parsedOptions["spark.driver.memory"] = utils.validateMemory(dmemory)
        parsedOptions["spark.executor.memory"] = utils.validateMemory(ememory)
        # For storing in database options must be a string
        self.options = json.dumps(parsedOptions)

        # Parse job configuration/options into list of values
        parsedJobConf = jobconf if isinstance(jobconf, ListType) else shlex.split(str(jobconf))
        self.jobconf = json.dumps(parsedJobConf)

        # Entrypoint for the Spark job
        self.entrypoint = utils.validateEntrypoint(entrypoint)
        # Jar file path
        self.jar = utils.validateJarPath(jar)

        # Properties with None default values (methods provided to set them)
        self.sparkappid = None
        self.starttime = None
        self.finishtime = None

    # Return deep copy of the job, note that this instance is not persistent in database
    def jobCopy(self, name, status, priority, createtime, submittime):
        # Create dummy job, we overwrite some parameters later, we also have to specify dummy
        # memory for driver and executors to pass validation. Eventually we just reassign the
        # same options from current job
        deepCopy = Job(name=name, status=status, priority=priority, createtime=createtime,
            submittime=submittime, entrypoint=self.entrypoint, jar=self.jar, dmemory="1g",
            ememory="1g", options={}, jobconf=[])
        # options below are completely overwritten
        deepCopy.options = self.options
        deepCopy.jobconf = self.jobconf
        # Options such as sparkappid, starttime, and finishtime will be set to None automatically
        return deepCopy

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
    def create(cls, session, **opts):
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
        session.add(job)
        session.commit()
        return job

    @classmethod
    @utils.sql
    def get(cls, session, uid):
        return session.query(cls).get(uid)

    @classmethod
    @utils.sql
    def list(cls, session, status, limit=100):
        query = session.query(cls)
        if status in cls.STATUSES:
            query = query.filter_by(status = status)
        limit = limit if limit > 0 else 1
        return query.order_by(desc(cls.createtime)).limit(limit).all()

    @classmethod
    @utils.sql
    def close(cls, session, job):
        if not job.canClose():
            raise StandardError("Cannot close job")
        job.status = cls.CLOSED
        session.commit()

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

    # Return shell command to execute as a list of arguments
    # Method allows to pass extra Spark options and additional job arguments to command line. These
    # options are transient, therefore are not saved for each job.
    def execCommand(self, sparkContext, extraArguments=[], extraSparkOptions={}):
        # `spark-submit --master sparkurl --conf "" --conf "" --class entrypoint jar`
        sparkSubmit = ["spark-submit"]
        # Note that name can be overwritten in Spark job itself, so when this job name will be
        # shown in Octohaven UI, Spark UI might display different name
        name = ["--name", "%s" % self.name]
        master = ["--master", "%s" % sparkContext.getMasterAddress()]
        # update options with `additionalOptions` argument
        confOptions = self.getSparkOptions().copy()
        confOptions.update(extraSparkOptions)
        # create list of conf options, ready to be used in cmd, flatten conf
        conf = [["--conf", "%s=%s" % (key, value)] for key, value in confOptions.items()]
        conf = [num for elem in conf for num in elem]
        entrypoint = ["--class", "%s" % self.entrypoint]
        jar = ["%s" % self.jar]
        # create list of job arguments, also append passed extra arguments
        jobConf = self.getJobConf() + extraArguments
        jobconf = ["%s" % elem for elem in jobConf]
        # construct exec command for shell
        cmd = sparkSubmit + name + master + conf + entrypoint + jar + jobconf
        return cmd
