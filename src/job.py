#!/usr/bin/env python

import re
from utils import *

STATUSES = ["CREATED", "WAITING", "SUBMITTED", "CLOSED"]
DURATIONS = ["LONG", "MEDIUM", "QUICK"]

class Job(object):
    def __init__(self, uid, status, starttime, name, duration, entrypoint, masterurl, options):
        if status not in STATUSES:
            raise StandardError("Status " + status + " is not supported")
        if duration not in DURATIONS:
            raise StandardError("Duration " + duration + " is not supported")
        # internal properties
        self.uid = uid
        self.status = status
        self.starttime = long(starttime)
        # Spark job properties
        self.name = name
        self.duration = duration
        self.entrypoint = self.validateEntrypoint(entrypoint)
        self.masterurl = self.validateMasterUrl(masterurl)
        self.options = {}
        # perform options check
        for (key, value) in options.items():
            if key == "spark.driver.memory" or key == "spark.executor.memory":
                self.options[key] = self.validateMemory(value)
            else:
                self.options[key] = value

    @private
    def validateMemory(self, value):
        groups = re.match(r"^(\d+)(k|kb|m|mb|g|gb|t|tb|p|pb)$", value.lower())
        if groups is None:
            raise StandardError("Memory value is incorrect: " + value)
        return groups.group(0)

    @private
    def validateEntrypoint(self, entrypoint):
        groups = re.match(r"^(\w+)(\.\w+)*$", entrypoint)
        if groups is None:
            raise StandardError("Entrypoint is incorrect: " + entrypoint)
        return groups.group(0)

    @private
    def validateMasterUrl(self, masterurl):
        groups = re.match(r"^spark://([\w\.-]+):\d+$", masterurl)
        if groups is None:
            raise StandardError("Master URL is incorrect: " + masterurl)
        return masterurl

    def updateStatus(self, newStatus):
        if newStatus not in STATUSES:
            raise StandardError("Status " + newStatus + " is not supported")
        self.status = newStatus

    def toDict(self):
        return {
            "uid": self.uid,
            "status": self.status,
            "starttime": self.starttime,
            "name": self.name,
            "duration": self.duration,
            "entrypoint": self.entrypoint,
            "masterurl": self.masterurl,
            "options": self.options
        }

    @classmethod
    def fromDict(cls, object):
        uid = object["uid"]
        status = object["status"]
        starttime = object["starttime"]
        name = object["name"]
        duration = object["duration"]
        entrypoint = object["entrypoint"]
        masterurl = object["masterurl"]
        options = object["options"]
        return cls(uid, status, starttime, name, duration, entrypoint, masterurl, options)
