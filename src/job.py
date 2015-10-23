#!/usr/bin/env python

import os, re
from types import IntType
from utils import *

# Job statuses that are supported
# Hierarchy of statuses:
# CREATED - job created to run as soon as possible
# DELAYED - job is delayed to run in n seconds
# WAITING - job is scheduled, and put into scheduler's pool
# FINISHED - job is finished, though it can be finished with different status in Spark
# CLOSED - job is closed before running
# Job can be closed as long as it's status is closable one
# CREATED / DELAYED -> WAITING -> CLOSED / RUNNING -> FINISHED

CREATED = "CREATED"
DELAYED = "DELAYED"
WAITING = "WAITING"
RUNNING = "RUNNING"
FINISHED = "FINISHED"
CLOSED = "CLOSED"
# list of all statuses
STATUSES = [CREATED, DELAYED, WAITING, RUNNING, FINISHED, CLOSED]
# list of statuses that use can close before they are submitted
CAN_CLOSE_STATUSES = [CREATED, DELAYED, WAITING]

# duration of the job
LONG = "LONG"
MEDIUM = "MEDIUM"
QUICK = "QUICK"
DURATIONS = [LONG, MEDIUM, QUICK]
# default priority for a job
DEFAULT_PRIORITY = 100
# job id key as a Spark job option
SPARK_UID_KEY = "spark.octohaven.jobId"

# Validation class to encapsulate all the checks that we have for Job and SparkJob
class JobCheck(object):
    @staticmethod
    def validateStatus(value):
        if value not in STATUSES:
            raise StandardError("Status " + str(value) + " is not supported")
        return value

    @staticmethod
    def validateJob(value):
        if type(value) is not Job:
            raise StandardError("Expected Job instance, got " + str(type(value)))
        return value

    @staticmethod
    def validatePriority(value):
        if type(value) is not IntType or value < 0:
            raise StandardError("Priority is incorrect: %s" % str(value))
        return value

    @staticmethod
    def validateMemory(value):
        groups = re.match(r"^(\d+)(k|kb|m|mb|g|gb|t|tb|p|pb)$", value.lower())
        if groups is None:
            raise StandardError("Memory value is incorrect: " + value)
        return groups.group(0)

    @staticmethod
    def validateEntrypoint(entrypoint):
        groups = re.match(r"^(\w+)(\.\w+)*$", entrypoint)
        if groups is None:
            raise StandardError("Entrypoint is incorrect: " + entrypoint)
        return groups.group(0)

    @staticmethod
    def validateMasterUrl(masterurl):
        groups = re.match(r"^spark://([\w\.-]+):\d+$", masterurl)
        if groups is None:
            raise StandardError("Master URL is incorrect: " + masterurl)
        return masterurl

    @staticmethod
    def validateUiUrl(uiurl):
        groups = re.match(r"^http://([\w\.-]+):\d+$", uiurl)
        if groups is None:
            raise StandardError("Spark UI URL is incorrect: " + uiurl)
        return uiurl

    @staticmethod
    def validateJarPath(jar):
        # do not validate on existence, only on path structure
        ok = os.path.isabs(jar) and jar.lower().endswith(".jar")
        if not ok:
            raise StandardError("Path " + jar + " is not valid")
        return jar

# Spark job to consolidate all the settings to launch spark-submit script
class SparkJob(object):
    def __init__(self, uid, name, masterurl, entrypoint, jar, options, jobconf=[]):
        self.uid = uid
        self.name = name
        self.masterurl = JobCheck.validateMasterUrl(masterurl)
        self.entrypoint = JobCheck.validateEntrypoint(entrypoint)
        self.jar = JobCheck.validateJarPath(jar)
        self.options = {}
        # jobconf is a job configuration relevant to the jar running,
        # another words, parameters for the main class of the jar
        self.jobconf = jobconf
        # perform options check
        for (key, value) in options.items():
            if key == "spark.driver.memory" or key == "spark.executor.memory":
                self.options[key] = JobCheck.validateMemory(value)
            else:
                self.options[key] = value

    def toDict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "masterurl": self.masterurl,
            "entrypoint": self.entrypoint,
            "jar": self.jar,
            "options": self.options,
            "jobconf": self.jobconf
        }

    # returns shell command to execute as a list of arguments
    # - additionalOptions => extra options to add to the execute command. They are transient and
    # therefor will not be saved as job options.
    def execCommand(self, additionalOptions={}):
        # spark-submit --master sparkurl --conf "" --conf "" --class entrypoint jar
        sparkSubmit = ["spark-submit"]
        name = ["--name", "%s" % self.name]
        master = ["--master", "%s" % self.masterurl]
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

    @classmethod
    def fromDict(cls, obj):
        uid = obj["uid"]
        name = obj["name"]
        masterurl = obj["masterurl"]
        entrypoint = obj["entrypoint"]
        jar = obj["jar"]
        options = obj["options"]
        jobconf = obj["jobconf"] if "jobconf" in obj else []
        return cls(uid, name, masterurl, entrypoint, jar, options, jobconf)

class Job(object):
    def __init__(self, uid, status, createtime, submittime, duration, sparkjob,
        priority=DEFAULT_PRIORITY):
        if duration not in DURATIONS:
            raise StandardError("Duration " + duration + " is not supported")
        if type(sparkjob) is not SparkJob:
            raise StandardError("Expected SparkJob, got " + str(type(sparkjob)))
        # internal properties
        self.uid = uid
        self.status = JobCheck.validateStatus(status)
        self.createtime = long(createtime)
        self.submittime = long(submittime)
        self.duration = duration
        # Spark job
        self.sparkjob = sparkjob
        # default job priority
        self.priority = JobCheck.validatePriority(priority)
        # Spark app id from Spark UI (if possible to fetch)
        self.sparkAppId = None

    def updateStatus(self, newStatus):
        self.status = JobCheck.validateStatus(newStatus)

    def updatePriority(self, newPriority):
        self.priority = JobCheck.validatePriority(newPriority)

    def updateSparkAppId(self, sparkAppId):
        self.sparkAppId = sparkAppId

    def toDict(self):
        return {
            "uid": self.uid,
            "status": self.status,
            "createtime": self.createtime,
            "submittime": self.submittime,
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
        uid = obj["uid"]
        status = obj["status"]
        createtime = obj["createtime"]
        submittime = obj["submittime"]
        duration = obj["duration"]
        sparkjob = SparkJob.fromDict(obj["sparkjob"])
        priority = obj["priority"] if "priority" in obj else DEFAULT_PRIORITY
        job = cls(uid, status, createtime, submittime, duration, sparkjob, priority)
        # discover whether we have Spark app id assigned to the job.
        if "sparkappid" in obj:
            job.updateSparkAppId(obj["sparkappid"])
        return job
