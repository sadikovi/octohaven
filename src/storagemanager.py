#!/usr/bin/env python

from redisconnector import RedisConnector
from job import Job
from utils import *

# Storage manager maintains history and addition of jobs
class StorageManager(object):
    ALL_JOBS_KEY = "ALL"

    def __init__(self, connector):
        if type(connector) is not RedisConnector:
            raise StandardError("Connector type " + str(type(connector)) + "is not supported")
        self.connector = connector

    @private
    def checkJob(self, job):
        if type(job) is not Job:
            raise StandardError("Expected Job instance, got " + str(type(job)))

    # returns Job instance, if key exists, otherwise None
    def jobForUid(self, uid):
        obj = self.connector.get(uid)
        return Job.fromDict(obj) if obj is not None else None

    def jobsForStatus(self, status, limit=20, sort=True, reverse=True):
        # set to default limit, so we never raise an error
        limit = 20 if not limit or limit < 0 else limit
        sort = True if sort is None else sort
        # fetch all job uids for that status
        jobs = self.connector.getCollection(status)
        # if collection is None, we return empty list, otherwise fetch jobs from that list
        if jobs is None:
            return []
        jobs = [self.jobForUid(uid) for uid in jobs]
        # ther are some situations where job is registered, but it is not saved. I think we should
        # filter out these cases
        jobs = [j for j in jobs if j is not None]
        if sort:
            # sort jobs by submit time in decreasing order (new jobs first)
            jobs = sorted(jobs, cmp=lambda x, y: cmp(x.submittime, y.submittime), reverse=reverse)
        return jobs[:limit]

    def allJobs(self, limit=20, sort=True):
        return self.jobsForStatus(self.ALL_JOBS_KEY, limit, sort)

    # save job and add it to global keyspace
    def saveJob(self, job):
        self.checkJob(job)
        self.connector.store(job.uid, job.toDict())
        self.addJobForStatus(self.ALL_JOBS_KEY, job.uid)

    def addJobForStatus(self, status, uid):
        self.connector.storeCollection(status, [uid])

    def removeJobFromStatus(self, status, uid):
        self.connector.removeFromCollection(status, [uid])

    # register job for a current status
    # if save is True, we also update job instance in Redis
    def registerJob(self, job, save=True):
        self.checkJob(job)
        if save:
            self.saveJob(job)
        self.addJobForStatus(job.status, job.uid)

    # remove job from current status (usually for an update)
    # if save is True, we also update job instance in Redis
    def unregisterJob(self, job, save=True):
        self.checkJob(job)
        # this looks a little bit of a concern and superfluous
        if save:
            self.saveJob(job)
        self.removeJobFromStatus(job.status, job.uid)
