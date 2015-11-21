#!/usr/bin/env python

from octolog import Octolog
from types import ListType
from utils import *

# delay interval for job creation in seconds, job will start within that interval
TIMETABLE_DELAY_INTERVAL = 60

# Timetable class to keep track of schedules for a particular job. Reports when to launch job, and
# keeps statistics of actual, and total number of jobs.
class Timetable(object):
    def __init__(self, uid, starttime, interval, active, jobid):
        self.uid = uid
        self.starttime = long(starttime)
        self.interval = long(interval)
        self.active = boolOrElse(active, False)
        # job uid of a template job, we need to clone it for every scheduled job
        self.jobid = jobid
        # these properties are never stored, since they are very dynamic, and should be
        # recalculated every time.
        self.numTotalJobs = int((currentTimeMillis() - starttime) / interval)
        self.numJobs = -1
        self.jobs = []

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
        starttime = obj["starttime"]
        interval = obj["interval"]
        active = obj["active"]
        jobid = obj["jobid"]
        return cls(uid, starttime, interval, active, jobid)

# Manager for timetables. Handles saving to and retrieving from storage, updates and etc.
class TimetableManager(Octolog, object):
    def init(self):
        pass

    # API to save job, this will create timetable and schedule job, similar to JobManager
    def saveJob(self, job):
        # create timetable with clone = job
        # increment job
        # save job similar to JobManager
        # spawn process to launch timetable process (if job is delayed)
        # spawn process to run job every interval
        # - clone job, e.g. change name, delay to be default timetable delay, ...
        # - increment job in timetable
        # - save job
        pass

    def cancel(self, tableid):
        pass
