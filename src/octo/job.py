#!/usr/bin/env python

import os, re, src.octo.utils as utils
from types import IntType, LongType

# Job statuses that are supported
# Hierarchy of statuses:
# READY - job is ready to be submitted in Spark
# DELAYED - job is delayed to run in N seconds
# RUNNING - job is currently running in Spark
# FINISHED - job is finished / killed, all we know is that it has exited
# CLOSED - job is closed before running
# Job can be closed as long as it's status is closable one
# (DELAYED -> ) READY -> RUNNING -> FINISHED
# +-----------------+ -> CLOSED

READY = "READY"
DELAYED = "DELAYED"
RUNNING = "RUNNING"
FINISHED = "FINISHED"
CLOSED = "CLOSED"
# list of all statuses
STATUSES = [READY, DELAYED, RUNNING, FINISHED, CLOSED]
# list of statuses that use can close before they are submitted
CLOSABLE_STATUSES = [READY, DELAYED]

# default priority for a job
DEFAULT_PRIORITY = 100

# finish time values (since job can be killed, so we do not have finish time for that)
# finish time when job is finished with status RUNNING, e.g. server was killed while running job
FINISH_TIME_UNKNOWN = -2L
# finish time when job has never been run before
FINISH_TIME_NONE = -1L

# Spark job to consolidate all the settings to launch spark-submit script
class SparkJob(object):
    def __init__(self, uid, name, entrypoint, jar, options, jobconf=[]):
        self.uid = uid
        self.name = name
        self.entrypoint = utils.validateEntrypoint(entrypoint)
        self.jar = utils.validateJarPath(jar)
        self.options = {}
        # perform options check
        for (key, value) in options.items():
            if key == "spark.driver.memory" or key == "spark.executor.memory":
                self.options[key] = utils.validateMemory(value)
            else:
                self.options[key] = value
        # jobconf is a job configuration relevant to the jar running, or parameters for the main
        # class of the jar
        self.jobconf = jobconf

    # returns shell command to execute as a list of arguments
    # - master => Spark Master URL, or "local[*]" for running in local mode
    # - additionalOptions => extra options to add to the execute command. They are transient and
    # therefor will not be saved as job options.
    def execCommand(self, master, additionalOptions={}):
        # spark-submit --master sparkurl --conf "" --conf "" --class entrypoint jar
        sparkSubmit = ["spark-submit"]
        name = ["--name", "%s" % self.name]
        master = ["--master", "%s" % master]
        # update options with `additionalOptions` argument
        confOptions = self.options.copy()
        confOptions.update(additionalOptions)
        # create list of conf options, ready to be used in cmd, flatten conf
        conf = [["--conf", "%s=%s" % (key, value)] for key, value in confOptions.items()]
        conf = [num for elem in conf for num in elem]
        entrypoint = ["--class", "%s" % self.entrypoint]
        jar = ["%s" % self.jar]
        # jobconf
        jobconf = ["%s" % elem for elem in self.jobconf]
        # construct exec command for shell
        cmd = sparkSubmit + name + master + conf + entrypoint + jar + jobconf
        return cmd


    def json(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "entrypoint": self.entrypoint,
            "jar": self.jar,
            "options": self.options,
            "jobconf": self.jobconf
        }

    def dict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "entrypoint": self.entrypoint,
            "jar": self.jar,
            "options": json.dumps(self.options),
            "jobconf": json.dumps(self.jobconf)
        }

    @classmethod
    def fromDict(cls, obj):
        # validate spark job uid to fetch only SparkJob instances
        uid = obj["uid"]
        name = obj["name"]
        entrypoint = obj["entrypoint"]
        jar = obj["jar"]
        options = utils.jsonOrElse(obj["options"], None)
        jobconf = utils.jsonOrElse(obj["jobconf"], None)
        if options is None:
            raise StandardError("Could not process options: %s" % obj["options"])
        if jobconf is None:
            raise StandardError("Could not process job configuration: %s" % obj["jobconf"])
        return cls(uid, name, entrypoint, jar, options, jobconf)

# Main abstraction in Octohaven. The primary properties are "name", "status", and "SparkJob"
# instance. Name is a duplicate of SparkJob instance, though later can be updated to be different,
# this was done mainly for the performance benefits, as we do need to go the fetch Spark job in
# order to just find out name. Job also maintains a few time states:
# - createtime -> time when job was actually created and stored in database
# - submittime -> time when job was actually submitted as command into Spark
# - finishtime -> time when job was identified as finished, it may not be exact time when job is
# finished in Spark. Also if we cannot resolve finish time, e.g. Octohaven was shut down while
# running a job and came up after three weeks, time will be set as "FINISH_TIME_UNKNOWN"
class Job(object):
    def __init__(self, uid, name, status, createtime, submittime, finishtime=FINISH_TIME_NONE,
        sparkjob, priority=DEFAULT_PRIORITY):
        utils.assertInstance(sparkjob, SparkJob)
        # internal properties
        self.uid = uid
        self.status = Job.checkStatus(status)
        self.createtime = long(createtime)
        self.submittime = long(submittime)
        # approximate time when job finished
        self.finishtime = long(finishtime)
        # Spark job
        self.sparkjob = sparkjob
        # default job priority is it's submittime, older jobs are executed first
        priority = self.submittime if priority == DEFAULT_PRIORITY else priority
        self.priority = utils.validatePriority(priority)
        # Spark app id from Spark UI (if possible to fetch)
        self.sparkAppId = None

    def updateStatus(self, newStatus):
        self.status = JobCheck.validateStatus(newStatus)

    def updatePriority(self, newPriority):
        self.priority = JobCheck.validatePriority(newPriority)

    def updateSparkAppId(self, sparkAppId):
        self.sparkAppId = sparkAppId

    # update start time when job actually got submitted to Spark
    # cannot be less than submittime
    def updateStartTime(self, newTime):
        assertType(newTime, LongType)
        newTime = self.submittime if newTime < self.submittime else newTime
        self.starttime = newTime

    # Job property "finishtime" indicates when approximately job finished, can have values "> 0" -
    # which is normal finish time, "== 0" - which is job has never been run, and "< 0", job is
    # finished, but we cannot resolve finish time
    def updateFinishTime(self, newTime):
        assertType(newTime, LongType)
        newTime = -1L if newTime < -1L else newTime
        self.finishtime = newTime

    # get current Spark job
    def getSparkJob(self):
        return self.sparkjob

    def toDict(self):
        return {
            "uid": self.uid,
            "status": self.status,
            "createtime": self.createtime,
            "submittime": self.submittime,
            "starttime": self.starttime,
            "finishtime": self.finishtime,
            "duration": self.duration,
            "sparkjob": self.sparkjob.toDict(),
            "priority": self.priority,
            "sparkappid": self.sparkAppId
        }

    # returns shell command to execute as a list of arguments
    # method exists for adding more functionality before/after executing Spark job
    def execCommand(self):
        # we add our own option with Spark job id, so we can resolve job -> Spark job connection
        # this option is hidden from user and should be updated and passed when we build cmd
        return self.sparkjob.execCommand({SPARK_UID_KEY: self.uid})

    @classmethod
    def fromDict(cls, obj):
        # validate uid, so we only fetch Job instances
        uid = JobCheck.validateJobUid(obj["uid"])
        status = obj["status"]
        createtime = obj["createtime"]
        submittime = obj["submittime"]
        duration = obj["duration"]
        sparkjob = SparkJob.fromDict(obj["sparkjob"])
        priority = obj["priority"] if "priority" in obj else DEFAULT_PRIORITY
        finishtime = obj["finishtime"] if "finishtime" in obj else FINISH_TIME_UNKNOWN
        starttime = obj["starttime"] if "starttime" in obj else -1L
        # create job with all the parameters
        job = cls(uid, status, createtime, submittime, duration, sparkjob, priority, finishtime,
            starttime)
        # discover whether we have Spark app id assigned to the job.
        if "sparkappid" in obj:
            job.updateSparkAppId(obj["sparkappid"])
        return job

    # Check if status is a valid one. Raise error, if wrong status is encountered.
    @staticmethod
    def checkStatus(status):
        if status not in STATUSES:
            raise StandardError("Status %s is wrong. Expected one of %s" % (status,
                ", ".join(STATUSES)))
        return status
