#!/usr/bin/env python

from redisconnector import RedisConnector
from job import Job

# Storage manager maintains history and addition of jobs
class StorageManager(object):
    ALL_JOBS_KEY = "ALL"

    def __init__(self, connector):
        if type(connector) is not RedisConnector:
            raise StandardError("Connector type " + str(type(connector)) + "is not supported")
        self.connector = connector

    # returns Job instance, if key exists, otherwise None
    def jobForUid(self, uid):
        obj = self.connector.get(uid)
        return Job.fromDict(obj) if obj is not None else None

    def jobsForStatus(self, status):
        # fetch all job uids for that status
        jobs = self.connector.getCollection(status)
        # if collection is None, we return empty list, otherwise fetch jobs from that list
        if jobs is None:
            return []
        return [self.jobForUid(uid) for uid in jobs]

    def allJobs(self):
        return self.jobsForStatus(self.ALL_JOBS_KEY)

    def saveJob(self, job):
        if type(job) is not Job:
            raise StandardError("Expected Job instance, got " + str(type(job)))
        self.connector.store(job.uid, job.toDict())

    def addJobForStatus(self, status, uid):
        self.connector.storeCollection(status, [uid])

    def removeJobFromStatus(self, status, uid):
        self.connector.removeFromCollection(status, [uid])
