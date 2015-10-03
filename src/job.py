#!/usr/bin/env python

STATUSES = ["CREATED", "WAITING", "SUBMITTED", "CLOSED"]
DURATIONS = ["LONG", "MEDIUM", "QUICK"]

class Job(object):
    def __init__(self, uid, status, starttime, name, duration, command):
        if status not in STATUSES:
            raise StandardError("Status " + status + " is not supported")
        if duration not in DURATIONS:
            raise StandardError("Duration " + duration + " is not supported")
        self.uid = uid
        self.status = status
        self.starttime = long(starttime)
        self.name = name
        self.duration = duration
        self.command = command

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
            "command": self.command
        }

    @classmethod
    def fromDict(cls, object):
        uid = object["uid"]
        status = object["status"]
        starttime = object["starttime"]
        name = object["name"]
        duration = object["duration"]
        command = object["command"]
        return cls(uid, status, starttime, name, duration, command)
