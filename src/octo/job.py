#!/usr/bin/env python

import src.octo.utils as utils
from types import LongType

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
TIME_UNKNOWN = -2L
# finish time when job has never been run before
TIME_NONE = -1L

# Main abstraction in Octohaven. The primary properties are "name", "status", and "SparkJob"
# reference. Name is a duplicate of SparkJob instance, though later can be updated to be different,
# this was done mainly for the performance benefits, as we do need to go the fetch Spark job in
# order to just find out name. Job also maintains a few time states:
# - createtime -> time when job was created and stored in database
# - submittime -> time when job was expected to be submitted into Spark
# - starttime -> time when job was actually submitted as command into Spark
# - finishtime -> time when job was identified as finished, it may not be exact time when job is
# finished in Spark. Also if we cannot resolve finish time, e.g. Octohaven was shut down while
# running a job and came up after, time will be set as "FINISH_TIME_UNKNOWN"
class Job(object):
    def __init__(self, uid, name, status, createtime, submittime, sparkjob,
        starttime=TIME_NONE, finishtime=TIME_NONE, priority=DEFAULT_PRIORITY):
        # internal properties
        self.uid = uid
        self.name = name
        self.status = Job.checkStatus(status)
        # time when job entry was created
        self.createtime = long(createtime)
        # time when job is supposed to run
        self.submittime = long(submittime)
        # actual time when job is submitted
        self.starttime = long(starttime)
        # approximate time when job is finished
        self.finishtime = long(finishtime)
        # Spark job uid as reference
        self.sparkjob = sparkjob
        # default job priority is it's submittime, older jobs are executed first
        priority = self.submittime if priority == DEFAULT_PRIORITY else priority
        self.priority = utils.validatePriority(priority)
        # Spark app id from Spark UI (if possible to fetch)
        self.sparkAppId = None

    def updateStatus(self, newStatus):
        self.status = Job.checkStatus(newStatus)

    def updatePriority(self, newPriority):
        self.priority = utils.validatePriority(newPriority)

    def updateSparkAppId(self, sparkAppId):
        self.sparkAppId = sparkAppId

    # Job property "starttime" indicates when job got actually submitted into Spark
    def updateStartTime(self, newTime):
        utils.assertInstance(newTime, LongType)
        self.starttime = newTime if newTime > TIME_UNKNOWN else TIME_UNKNOWN

    # Job property "finishtime" indicates when approximately job finished, can have values ">= 0" -
    # which is normal finish time, "-1" - which is job has never been run, and "-2", job is
    # finished, but we cannot resolve finish time
    def updateFinishTime(self, newTime):
        utils.assertInstance(newTime, LongType)
        self.finishtime = newTime if newTime > TIME_UNKNOWN else TIME_UNKNOWN

    def json(self):
        return self.dict()

    def dict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "status": self.status,
            "createtime": self.createtime,
            "submittime": self.submittime,
            "starttime": self.starttime,
            "finishtime": self.finishtime,
            "sparkjob": self.sparkjob,
            "priority": self.priority,
            "sparkappid": self.sparkAppId
        }

    @classmethod
    def fromDict(cls, obj):
        uid = obj["uid"]
        name = obj["name"]
        status = obj["status"]
        createtime = obj["createtime"]
        submittime = obj["submittime"]
        sparkjob = obj["sparkjob"]
        starttime = obj["starttime"] if "starttime" in obj else TIME_UNKNOWN
        finishtime = obj["finishtime"] if "finishtime" in obj else TIME_UNKNOWN
        priority = obj["priority"] if "priority" in obj else DEFAULT_PRIORITY
        # create job with all the parameters
        job = cls(uid, name, status, createtime, submittime, sparkjob,
            starttime, finishtime, priority)
        # discover whether we have Spark app id assigned to the job.
        if "sparkappid" in obj:
            job.updateSparkAppId(obj["sparkappid"])
        return job

    # Check if status is a valid one. Raise error, if wrong status is encountered.
    @staticmethod
    def checkStatus(status):
        if status not in STATUSES:
            msg = "Status %s is wrong. Expected one of %s" % (status, ", ".join(STATUSES))
            raise StandardError(msg)
        return status
