#!/usr/bin/env python

from octolog import Octolog
from types import ListType
from job import SparkJob, Job
from jobmanager import JobManager
from utils import *

# delay interval for job creation in seconds, job will start within that interval
TIMETABLE_DELAY_INTERVAL = 60
TIMETABLE_KEYSPACE = "TIMETABLE_KEYSPACE"

# Timetable class to keep track of schedules for a particular job. Reports when to launch job, and
# keeps statistics of actual, and total number of jobs.
# Interval is dynamic, and represented as a list of intervals in seconds, e.g. [60, 120, 60], which
# means "run first job after 1 minute, second job in 2 minutes after launching first job, etc."
# If list is out of bound, we repeat intervals. This will allow us to schedule more complex times,
# e.g. running only on Saturday, Sunday, or running every work day at 2pm.
# - starttime - time in milliseconds
# - intervals - intervals in seconds
# - jobs - list of job uids
class Timetable(object):
    def __init__(self, uid, name, canceled, clonejobid, starttime, intervals, jobs):
        if type(intervals) is not ListType:
            raise StandardError("Expected intervals as ListType, got " + str(type(intervals)))
        if type(jobs) is not ListType:
            raise StandardError("Expected jobs as ListType, got " + str(type(jobs)))
        self.uid = uid
        self.name = str(name)
        self.canceled = bool(canceled)
        # job uid of a template job, we need to clone it for every scheduled job
        self.clonejobid = clonejobid
        self.starttime = long(starttime)
        self.intervals = intervals
        # these properties are never stored, since they are very dynamic, and should be
        # recalculated every time.
        self.numTotalJobs = Timetable.numJobs((currentTimeMillis() - starttime) / 1000, intervals)
        # list of job uids
        self.jobs = jobs
        self.numJobs = len(jobs)

    @staticmethod
    @private
    def numJobs(period, intervals):
        sm = sum(intervals)
        ln = len(intervals)
        if sm <= 0:
            return 0
        if period < sm:
            nt = 0
            for i in range(ln):
                nt += intervals[i]
                if nt > period:
                    return i
            return 0
        else:
            jobs = (period / sm) * ln
            diff = period % sm
            return jobs + Timetable.numJobs(diff, intervals)

    # increment counter of total jobs and append job to the list
    def incrementJob(self, jobid):
        self.numTotalJobs += 1
        self.numJobs += 1
        self.jobs.append(jobid)

    def toDict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "canceled": self.canceled,
            "clonejobid": self.clonejobid,
            "starttime": self.starttime,
            "intervals": self.intervals,
            "numtotaljobs": self.numTotalJobs,
            "numjobs": self.numJobs,
            "jobs": self.jobs
        }

    @classmethod
    def fromDict(cls, obj):
        uid = obj["uid"]
        name = obj["name"]
        canceled = obj["canceled"]
        clonejobid = obj["clonejobid"]
        starttime = obj["starttime"]
        intervals = obj["intervals"]
        jobs = obj["jobs"]
        return cls(uid, name, canceled, clonejobid, starttime, intervals, jobs)

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
        return self.jobManager.createJob(sparkjob, TIMETABLE_DELAY_INTERVAL)

    # creates new timetable using `delay` in seconds for starting timetable,
    # `intervals` is a list of intervals in seconds
    def createTimetable(self, name, delay, intervals, job):
        uid = nextTimetableId()
        if type(job) is not Job:
            raise StandardError("Expected Job, got " + str(type(job)))
        delay = 0 if delay <= 0 else delay
        start = currentTimeMillis() + delay * 1000
        return Timetable(uid, name, False, job.uid, start, intervals, [])

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
    def listTimetables(self):
        def func(x, y):
            return cmp(x.name, y.name)
        return self.storageManager.itemsForKeyspace(TIMETABLE_KEYSPACE, -1, func, klass=Timetable)

    # cancel timetable, set `active` status to False
    def cancel(self, uid):
        timetable = self.timetableForUid(uid)
        if not timetable:
            raise StandardError("Timetable with uid '%s' does not exist" % uid)
        if timetable.canceled:
            raise StandardError("Cannot cancel already canceled timetable with uid '%s'" % uid)
        timetable.canceled = True
        self.saveTimetable(timetable)
