#!/usr/bin/env python

from redisconnector import RedisConnector
from job import Job, JobCheck
from utils import *

# Storage manager maintains history and addition of jobs
class StorageManager(object):
    def __init__(self, connector):
        if type(connector) is not RedisConnector:
            raise StandardError("Connector type " + str(type(connector)) + "is not supported")
        self.connector = connector

    # returns Job instance, if key exists, otherwise None
    def jobForUid(self, uid):
        obj = self.connector.get(uid)
        return None if not obj else Job.fromDict(obj)

    # retrieving jobs for a particular status with limit and sorting
    # - status => job status to fetch, e.g. CREATED, WAITING
    # - limit => limit results by the number provided, if limit is less than 0, return all results
    # - cmpFunc => comparison function, see Python documentation for details
    def jobsForStatus(self, status, limit=30, cmpFunc=None):
        doLimit = limit >= 0
        doSort = cmp is not None
        # fetch all job uids for that status
        jobUids = self.connector.getCollection(status)
        jobs = [self.jobForUid(uid) for uid in jobUids] if jobUids else []
        # filter out jobs that are None, this can happen when job is registered, but it is not
        # saved. This is a rare case, but we should filter them in order to avoid confusion
        jobs = [job for job in jobs if job is not None]
        # perform sorting using cmp
        jobs = sorted(jobs, cmp=cmpFunc) if doSort else jobs
        # limit results if possible
        jobs = jobs[:limit] if doLimit else jobs
        return jobs

    # save job
    def saveJob(self, job):
        JobCheck.validateJob(job)
        self.connector.store(job.uid, job.toDict())

    def addJobForStatus(self, status, uid):
        self.connector.storeCollection(status, [uid])

    def removeJobFromStatus(self, status, uid):
        self.connector.removeFromCollection(status, [uid])
