#!/usr/bin/env python

from octolog import Octolog
from types import ListType, IntType, LongType
from job import SparkJob, Job
from jobmanager import JobManager
from crontab import CronTab
from utils import *

TIMETABLE_KEYSPACE = "TIMETABLE_KEYSPACE"
DEFAULT_TIMETABLE_NAME = "Just another timetable"
# statuses for timetable
# active - timetable is active and launching jobs on schedule
TIMETABLE_ACTIVE = "ACTIVE"
# paused - timetable is stopped, no jobs launched, can be resumed
TIMETABLE_PAUSED = "PAUSED"
# canceled - timetable is canceled, no future jobs expected, cannot be resumed
TIMETABLE_CANCELED = "CANCELED"
# list of statuses
TIMETABLE_STATUSES = [TIMETABLE_ACTIVE, TIMETABLE_PAUSED, TIMETABLE_CANCELED]

class TimetableCheck(object):
    @staticmethod
    def validateStatus(status):
        if status not in TIMETABLE_STATUSES:
            raise StandardError("Invalid status for Timetable")
        return status

# Timetable class to keep track of schedules for a particular job. Reports when to launch job, and
# keeps statistics of total number of jobs. Uses cron expression to specify scheduling time
class Timetable(object):
    def __init__(self, uid, name, status, clonejobid, crontab, starttime, stoptime, jobs,
        latestruntime=-1):
        self.uid = uid
        name = str(name).strip()
        self.name = name if len(name) > 0 else DEFAULT_TIMETABLE_NAME
        self.status = TimetableCheck.validateStatus(status)
        # job uid of a template job, we need to clone it for every scheduled job
        self.clonejobid = clonejobid
        if type(crontab) is not CronTab:
            raise StandardError("Expected CronTab, got %s" % str(type(crontab)))
        self.crontab = crontab
        # start and stop time in milliseconds
        self.starttime = long(starttime)
        self.stoptime = long(stoptime)
        if type(jobs) is not ListType:
            raise StandardError("Expected ListType, got %s" % str(type(jobs)))
        self.jobs = jobs
        # we do not store number of jobs, since we can compute it using list
        self.numJobs = len(jobs)
        self.latestjobid = jobs[-1] if self.numJobs > 0 else None
        self.latestruntime = long(latestruntime)

    # increment counter of total jobs and append job to the list
    def addJob(self, job):
        if type(job) is not Job:
            raise StandardError("Expected Job, got %s" % str(type(job)))
        self.numJobs += 1
        self.jobs.append(job.uid)
        self.latestjobid = job.uid

    # update latest run time, when timetable was invoked to create new job
    def updateRunTime(self, timestamp):
        self.latestruntime = long(timestamp)

    def toDict(self, includejobs=True):
        return {
            "uid": self.uid,
            "name": self.name,
            "status": self.status,
            "clonejobid": self.clonejobid,
            "crontab": self.crontab.toDict(),
            "starttime": self.starttime,
            "stoptime": self.stoptime,
            "numjobs": self.numJobs,
            "jobs": self.jobs if includejobs else None,
            "latestjobid": self.latestjobid,
            "latestruntime": self.latestruntime
        }

    @classmethod
    def fromDict(cls, obj):
        uid = obj["uid"]
        name = obj["name"]
        status = obj["status"]
        clonejobid = obj["clonejobid"]
        crontab = CronTab.fromDict(obj["crontab"])
        starttime = obj["starttime"]
        stoptime = obj["stoptime"]
        jobs = obj["jobs"]
        # latest run time, slightly different from job creation
        latestruntime = obj["latestruntime"] if "latestruntime" in obj else -1
        return cls(uid, name, status, clonejobid, crontab, starttime, stoptime, jobs, latestruntime)

# Manager for timetables. Handles saving to and retrieving from storage, updates and etc.
class TimetableManager(Octolog, object):
    def __init__(self, jobManager):
        if type(jobManager) is not JobManager:
            raise StandardError("Expected JobManager, got " + str(type(jobManager)))
        self.jobManager = jobManager
        self.storageManager = jobManager.storageManager

    @private
    def cloneSparkJob(self, sparkjob):
        if type(sparkjob) is not SparkJob:
            raise StandardError("Expected SparkJob, got " + str(type(sparkjob)))
        # `SparkJob::clone()` already returns new instance with updated uid
        newSparkjob = sparkjob.clone()
        return newSparkjob

    @private
    def cloneJob(self, job):
        # creates clone of the job, with different uids
        if type(job) is not Job:
            raise StandardError("Expected Job, got " + str(type(job)))
        # duplicate fields and replace uids
        sparkjob = self.cloneSparkJob(job.sparkjob)
        return self.jobManager.createJob(sparkjob, delay=0)

    # creates new timetable using `delay` in seconds for starting timetable,
    # `intervals` is a list of intervals in seconds
    def createTimetable(self, name, crontab, clonejob):
        if type(clonejob) is not Job:
            raise StandardError("Expected Job, got " + str(type(clonejob)))
        uid = nextTimetableId()
        # current time in milliseconds
        starttime = currentTimeMillis()
        # stop time is negative as it is active
        stoptime = -1
        status = TIMETABLE_ACTIVE
        return Timetable(uid, name, status, clonejob.uid, crontab, starttime, stoptime, [])

    def saveTimetable(self, timetable):
        # use storage manager to save timetable
        # add timetable id to the set
        # start process for that timetable
        if type(timetable) is not Timetable:
            raise StandardError("Expected Timetable, got " + str(type(timetable)))
        self.storageManager.saveItem(timetable, klass=Timetable)
        self.storageManager.addItemToKeyspace(TIMETABLE_KEYSPACE, timetable.uid)

    def timetableForUid(self, uid):
        return self.storageManager.itemForUid(uid, klass=Timetable)

    # we do not limit timetables and return all of them sorted by name
    # filtering by status is done by fetching everything and filtering by status
    # we do not store timetable for status (like jobs), because we do not expect that many
    # timetables, complexity of fast updates, and maintenance
    def listTimetables(self, statuses=TIMETABLE_STATUSES):
        if type(statuses) is not ListType:
            raise StandardError("Expected ListType, got %s" % str(type(statuses)))
        # normalize statuses
        statuses = [str(x).upper() for x in statuses]
        def func(x, y):
            return cmp(x.name, y.name)
        # we do not sort when fetching from storage, as it can be expensive, sort only objects
        # that we will send back
        arr = self.storageManager.itemsForKeyspace(TIMETABLE_KEYSPACE, -1, None, klass=Timetable)
        filtered = sorted([x for x in arr if x.status in statuses], cmp=func)
        return filtered

    # resume current timetable
    def resume(self, timetable):
        if type(timetable) is not Timetable:
            raise StandardError("Expected Timetable, got " + str(type(timetable)))
        if timetable.status == TIMETABLE_ACTIVE:
            raise StandardError("Cannot resume already active timetable")
        if timetable.status == TIMETABLE_CANCELED:
            raise StandardError("Cannot resume canceled timetable")
        timetable.status = TIMETABLE_ACTIVE
        self.saveTimetable(timetable)

    # pause current timetable, you can resume it later
    def pause(self, timetable):
        if type(timetable) is not Timetable:
            raise StandardError("Expected Timetable, got " + str(type(timetable)))
        if timetable.status == TIMETABLE_PAUSED:
            raise StandardError("Cannot pause already paused timetable")
        if timetable.status == TIMETABLE_CANCELED:
            raise StandardError("Cannot pause canceled timetable")
        timetable.status = TIMETABLE_PAUSED
        self.saveTimetable(timetable)

    # cancel timetable, you will not be able to revoke it
    def cancel(self, timetable):
        if type(timetable) is not Timetable:
            raise StandardError("Expected Timetable, got " + str(type(timetable)))
        if timetable.status == TIMETABLE_CANCELED:
            raise StandardError("Cannot cancel canceled timetable")
        timetable.status = TIMETABLE_CANCELED
        timetable.stoptime = currentTimeMillis()
        self.saveTimetable(timetable)
