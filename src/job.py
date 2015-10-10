#!/usr/bin/env python

import os, re
from utils import *

STATUSES = ["CREATED", "WAITING", "SUBMITTED", "CLOSED"]
DURATIONS = ["LONG", "MEDIUM", "QUICK"]

class JobCheck(object):
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
    def validateJarPath(jar):
        ok = os.path.isabs(jar) and os.path.exists(jar) and jar.lower().endswith(".jar")
        if not ok:
            raise StandardError("Path " + jar + " is not valid")
        return jar

class SparkJob(object):
    def __init__(self, uid, name, masterurl, entrypoint, jar, options):
        self.uid = uid
        self.name = name
        self.masterurl = JobCheck.validateMasterUrl(masterurl)
        self.entrypoint = JobCheck.validateEntrypoint(entrypoint)
        self.jar = JobCheck.validateJarPath(jar)
        self.options = {}
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
            "options": self.options
        }

    @classmethod
    def fromDict(cls, object):
        uid = object["uid"]
        name = object["name"]
        masterurl = object["masterurl"]
        entrypoint = object["entrypoint"]
        jar = object["jar"]
        options = object["options"]
        return cls(uid, name, masterurl, entrypoint, jar, options)

class Job(object):
    def __init__(self, uid, status, starttime, duration, sparkjob):
        if status not in STATUSES:
            raise StandardError("Status " + status + " is not supported")
        if duration not in DURATIONS:
            raise StandardError("Duration " + duration + " is not supported")
        if type(sparkjob) is not SparkJob:
            raise StandardError("Expected SparkJob, got " + str(type(sparkjob)))
        # internal properties
        self.uid = uid
        self.status = status
        self.starttime = long(starttime)
        self.duration = duration
        # Spark job
        self.sparkjob = sparkjob

    def updateStatus(self, newStatus):
        if newStatus not in STATUSES:
            raise StandardError("Status " + newStatus + " is not supported")
        self.status = newStatus

    def toDict(self):
        return {
            "uid": self.uid,
            "status": self.status,
            "starttime": self.starttime,
            "duration": self.duration,
            "sparkjob": self.sparkjob.toDict()
        }

    @classmethod
    def fromDict(cls, object):
        uid = object["uid"]
        status = object["status"]
        starttime = object["starttime"]
        duration = object["duration"]
        sparkjob = SparkJob.fromDict(object["sparkjob"])
        return cls(uid, status, starttime, duration, sparkjob)
