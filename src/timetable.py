#!/usr/bin/env python

from octolog import Octolog
from types import ListType
from job import SparkJob, Job
from jobmanager import JobManager
from utils import *

# delay interval for job creation in seconds, job will start within that interval
TIMETABLE_DELAY_INTERVAL = 60
TIMETABLE_KEYSPACE = "TIMETABLE_KEYSPACE"
TIMETABLE_JOBS_SUFFIX = ":jobs"

# Timetable class to keep track of schedules for a particular job. Reports when to launch job, and
# keeps statistics of actual, and total number of jobs.
# Interval is dynamic, and represented as a list of intervals in seconds, e.g. [60, 120, 60], which
# means "run first job after 1 minute, second job in 2 minutes after launching first job, etc."
# If list is out of bound, we repeat intervals. This will allow us to schedule more complex times,
# e.g. running only on Saturday, Sunday, or running every work day at 2pm.
class Timetable(object):
    def __init__(self, uid, name, starttime, interval, active, jobid):
        self.uid = uid
        self.name = str(name)
        self.starttime = long(starttime)
        if type(interval) is not ListType:
            raise StandardError("Expected ListType interval, got " + str(type(interval)))
        self.interval = interval
        self.active = boolOrElse(active, False)
        # job uid of a template job, we need to clone it for every scheduled job
        self.jobid = jobid
        # these properties are never stored, since they are very dynamic, and should be
        # recalculated every time.
        self.numTotalJobs = self.numJobs(currentTimeMillis() - starttime, interval)
        self.numJobs = -1
        # list of job uids
        self.jobs = []

    @private
    def numJobs(self, period, intervals):
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
            return jobs + numJobs(diff, intervals)

    # update jobs after creation, also update counter
    def updateJobs(self, jobs):
        if type(jobs) is not ListType:
            raise StandardError("Expected ListType, got " + str(type(jobs)))
        self.jobs = jobs
        self.numJobs = len(self.jobs)

    # increment counter of total jobs and append job to the list
    def incrementJob(self, jobid):
        self.numTotalJobs += 1
        self.jobs.append(jobid)

    def toDict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "starttime": self.starttime,
            "interval": self.interval,
            "active": self.active,
            "jobid": self.jobid,
            "numtotaljobs": self.numTotalJobs,
            "numjobs": self.numJobs
        }

    @classmethod
    def fromDict(cls, obj):
        uid = obj["uid"]
        name = obj["name"]
        starttime = obj["starttime"]
        interval = obj["interval"]
        active = obj["active"]
        jobid = obj["jobid"]
        return cls(uid, name, starttime, interval, active, jobid)

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
        return JobManager.createJob(sparkjob, TIMETABLE_DELAY_INTERVAL)

    def createTimetable(name, start, interval, job):
        uid = nextTimetableId()
        if type(job) is not Job:
            raise StandardError("Expected Job, got " + str(type(job)))
        return TimeTable(uid, name, start, interval, True, job.uid)

    def saveTimetable(self, timetable):
        # use storage manager to save timetable
        # add timetable id to the set
        # start process for that timetable
        if type(timetable) is not Timetable:
            raise StandardError("Expected Timetable, got " + str(type(timetable)))
        self.storageManager.saveItem(timetable, klass=Timetable)
        self.storageManager.addItemToKeyspace(TIMETABLE_KEYSPACE, timetable.uid)
        self.storageManager.addItemsToKeyspace(timetable.uid + TIMETABLE_JOBS_SUFFIX,
            timetable.jobs)

    @private
    def jobsForTimetable(self, timetable):
        return self.storageManager.itemsForKeyspace(timetable.uid + TIMETABLE_JOBS_SUFFIX, -1)

    def timetableForUid(self, uid):
        timetable = self.storageManager.itemForUid(uid, klass=Timetable)
        if timetable:
            jobs = jobsForTimetable(timetable)
            timetable.updateJobs(jobs)
        return timetable

    # we do not limit timetables and return all of them sorted by name
    def listTimetables(self):
        def func(x, y):
            return cmp(x.name, y.name)
        tables = self.storageManager.itemsForKeyspace(TIMETABLE_KEYSPACE, -1, func, klass=Timetable)
        for t in tables:
            jobs = jobsForTimetable(t)
            t.updateJobs(jobs)
        return tables

    # cancel timetable, set `active` status to False
    def cancel(self, uid):
        timetable = self.timetableForUid(uid)
        if not timetable:
            raise StandardError("Timetable with uid '%s' does not exist" % uid)
        if not timetable.active:
            raise StandardError("Cannot cancel non-active timetable with uid '%s'" % uid)
        timetable.active = False
        self.saveTimetable(timetable)
