#!/usr/bin/env python

from types import IntType
from storagemanager import StorageManager
from utils import *

# super simple scheduler to run Spark jobs in background
class Scheduler(object):
    def __init__(self, storageManager, poolSize):
        if type(poolSize) is not IntType:
            raise StandardError("Expected IntType, got " + str(type(poolSize)))
        if type(storageManager) is not StorageManager:
            raise StandardError("Expected StorageManager, got " + str(type(storageManager)))
        self.poolSize = poolSize
        self.storageManager = storageManager

    @private
    def fetchStatus(self, status):
        return self.storageManager.jobsForStatus(status, limit=self.poolSize,
            sort=True, reverse=False)

    def fetch(self):
        arr = self.fetchStatus("WAITING")
        if len(arr) < poolSize:
            # we have to check created jobs
            add = self.fetchStatus("CREATED")
            return arr + add
        # otherwise just return an array of waiting jobs
        return arr
