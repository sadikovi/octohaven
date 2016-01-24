#!/usr/bin/env python

import src.octo.utils as utils
from octolog import Octolog
from src.octo.subscription import Emitter
from src.octo.crontab import CronTab

TIMETABLE_KEYSPACE = "TIMETABLE_KEYSPACE"
DEFAULT_TIMETABLE_NAME = "Another timetable"
# statuses for timetable
# active - timetable is active and launching jobs on schedule
TIMETABLE_ACTIVE = "ACTIVE"
# paused - timetable is stopped, no jobs launched, can be resumed
TIMETABLE_PAUSED = "PAUSED"
# cancelled - timetable is cancelled, no future jobs expected, cannot be resumed
TIMETABLE_CANCELLED = "CANCELLED"
# list of statuses
TIMETABLE_STATUSES = [TIMETABLE_ACTIVE, TIMETABLE_PAUSED, TIMETABLE_CANCELLED]

class TimetableCheck(object):
    @staticmethod
    def validateStatus(status):
        if status not in TIMETABLE_STATUSES:
            raise StandardError("Invalid status for Timetable")
        return status

# Timetable class to keep track of schedules for a particular job. Reports when to launch job, and
# keeps statistics of total number of jobs. Uses cron expression to specify scheduling time
class Timetable(object):
    def __init__(self, uid, name, status, clonejob, crontab, starttime, stoptime):
        self.uid = uid
        self.name = name
        self.status = TimetableCheck.validateStatus(status)
        # job uid of a template job, we need to clone it for every scheduled job
        self.clonejob = clonejob
        # start and stop time in milliseconds
        self.starttime = long(starttime)
        self.stoptime = long(stoptime)
        # assign crontab
        utils.assertInstance(crontab, CronTab)
        self.crontab = crontab

    def json(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "status": self.status,
            "clonejob": self.clonejob,
            "crontab": self.crontab.dict(),
            "starttime": self.starttime,
            "stoptime": self.stoptime
        }

    def dict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "status": self.status,
            "clonejob": self.clonejob,
            "starttime": self.starttime,
            "stoptime": self.stoptime,
            "cron_pattern": self.crontab.pattern
        }

    @classmethod
    def fromDict(cls, obj):
        uid = obj["uid"]
        name = obj["name"]
        status = obj["status"]
        clonejob = obj["clonejob"]
        crontab = CronTab.fromPattern(obj["cron_pattern"])
        starttime = obj["starttime"]
        stoptime = obj["stoptime"]
        return cls(uid, name, status, clonejob, crontab, starttime, stoptime)

# Manager for timetables. Handles saving to and retrieving from storage, updates and etc.
class TimetableManager(Emitter, object):
    def __init__(self, storageManager):
        utils.assertInstance(storageManager, StorageManager)
        self.storage = storageManager
        # register as emitter
        Emitter.__init__(self, GLOBAL_DISPATCHER)

    # creates new timetable using `delay` in seconds for starting timetable,
    # `intervals` is a list of intervals in seconds
    def createTimetable(self, name, crontab, clonejob):
        utils.assertInstance(clonejob, Job)
        utils.assertInstance(crontab, CronTab)
        # resolve name
        name = str(name).strip() if len(str(name).strip()) > 0 else DEFAULT_TIMETABLE_NAME
        # current time in milliseconds
        starttime = utils.currentTimeMillis()
        # stop time is negative as it is active
        stoptime = -1L
        status = TIMETABLE_ACTIVE
        timetable = Timetable(None, name, status, clonejob.uid, crontab, starttime, stoptime)
        dct = timetable.dict()
        dct["uid"] = self.storage.createTimetable(dct)
        return Timetable.fromDict(dct)

    def timetableForUid(self, uid):
        dct = self.storage.getTimetable(uid)
        return None if not dct else Timetable.fromDict(dct)

    # status None indicates that we fetch all statuses
    def listTimetables(self, status):
        if status is not None and status not in TIMETABLE_STATUSES:
            raise StandardError("Status '%s' is not valid" % status)
        return self.storage.getTimetables(status)

    # resume current timetable
    def resume(self, timetable):
        utils.assertInstance(timetable, Timetable)
        if timetable.status == TIMETABLE_ACTIVE:
            raise StandardError("Cannot resume already active timetable")
        if timetable.status == TIMETABLE_CANCELLED:
            raise StandardError("Cannot resume cancelled timetable")
        timetable.status = TIMETABLE_ACTIVE
        self.storage.updateTimetable(timetable.dict())

    # pause current timetable, you can resume it later
    def pause(self, timetable):
        utils.assertInstance(timetable, Timetable)
        if timetable.status == TIMETABLE_PAUSED:
            raise StandardError("Cannot pause already paused timetable")
        if timetable.status == TIMETABLE_CANCELLED:
            raise StandardError("Cannot pause cancelled timetable")
        timetable.status = TIMETABLE_PAUSED
        self.storage.updateTimetable(timetable.dict())

    # cancel timetable, you will not be able to revoke it
    def cancel(self, timetable):
        utils.assertInstance(timetable, Timetable)
        if timetable.status == TIMETABLE_CANCELLED:
            raise StandardError("Cannot cancel cancelled timetable")
        timetable.status = TIMETABLE_CANCELLED
        timetable.stoptime = utils.currentTimeMillis()
        self.storage.updateTimetable(timetable.dict())
