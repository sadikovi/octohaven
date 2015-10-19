#!/usr/bin/env python

import time
from Queue import PriorityQueue
from types import IntType
from threading import Timer, Lock
from subprocess import Popen
from job import Job, DEFAULT_PRIORITY
from redisconnector import RedisConnector, RedisConnectionPool
from storagemanager import StorageManager
import sparkheartbeat
from utils import *

# create lock, it is unnecessary, because of GIL, but it is safe to have it anyway.
lock = Lock()

#################################################################
# Global functions to fetch and run jobs                        #
#################################################################

# method populates queue with fresh jobs with statuses WAITING and CREATED
def fetch(scheduler):
    try:
        lock.acquire()
        # current time in milliseconds
        currTime = long(time.time() * 1000)
        # calculate min and max boundaries for checking delayed job
        minT, maxT = currTime - scheduler.fetchInterval/10, currTime + scheduler.fetchInterval
        # Pre-step of checking DELAYED jobs. We need to check them every time, fetch runs, because
        # we do not want to miss the window. fetch 50 times pool size jobs (should be changed)
        print "[INFO] Checking DELAYED jobs"
        delayed = scheduler.fetchStatus("DELAYED", scheduler.poolSize * 50)
        print "[INFO] Fetched %s DELAYED jobs" % str(len(delayed))
        if len(delayed) > 0:
            # update status on waiting and priority
            # in this case we also fetch jobs that were overdue and not necessary need to be run.
            due = [j for j in delayed if j and j.submittime <= maxT]
            for dueJob in due:
                print "[WARN] Updated job %s to run as soon as possible" % dueJob.uid
                scheduler.storageManager.unregisterJob(dueJob, save=False)
                dueJob.updateStatus("WAITING")
                dueJob.updatePriority(dueJob.priority - 1)
                scheduler.storageManager.registerJob(dueJob)
        # proper scheduling fetch
        # fetches WAITING jobs first, sorting them by priority, then CREATED, if we have free slots.
        # if there is a delayed job that was updated as waiting, it will be queued and run as fast
        # as possible. If pool is full, then we will have to wait for the next free slot.
        numJobs = scheduler.poolSize - scheduler.pool.qsize()
        if numJobs > 0:
            print "[INFO] Requesting %s jobs" % str(numJobs)
            arr = scheduler.fetchStatus("WAITING", numJobs)
            if len(arr) < numJobs:
                numJobs = numJobs - len(arr)
                # we have to check created jobs
                add = scheduler.fetchStatus("CREATED", numJobs)
                arr = arr + add
            for job in arr:
                scheduler.add(job, job.priority)
        else:
            print "[INFO] No new jobs were added"
        print "[INFO] Updated queue size: %s" % str(scheduler.pool.qsize())
    finally:
        lock.release()
        # create timer for a subsequent lookup
        fetchTimer = Timer(scheduler.fetchInterval, fetch, [scheduler])
        fetchTimer.daemon = True
        fetchTimer.start()

# takes job from the queue and executes it
def runJob(scheduler):
    try:
        lock.acquire()
        status = sparkheartbeat.sparkStatus(scheduler.sparkurl)
        if status < 0:
            msg = "busy" if status == -1 else "unreachable"
            print "[WARN] Cluster is %s. Will try again later" % msg
        else:
            print "[INFO] Cluster is free. Fetching job from a queue..."
            job = None
            while scheduler.hasNext() and not job:
                job = scheduler.get()
                # refresh status of the job
                verify = scheduler.storageManager.jobForUid(job.uid)
                if not verify or verify.status != job.status:
                    print "[ERROR] Could not resolve job. Fetching next"
                    job = None
                    continue
            if not job:
                print "[INFO] There are no jobs available in scheduler pool"
            else:
                print "[INFO] Submitting the job"
                scheduler.storageManager.unregisterJob(job, save=False)
                job.updateStatus("SUBMITTED")
                scheduler.storageManager.registerJob(job)
                cmd = job.execCommand()
                print "[INFO] Executing command: %s" % str(cmd)
                # run command with NO_WAIT
                Popen(cmd).pid
    finally:
        lock.release()
        # prepare timer for a subsequent operation
        runTimer = Timer(scheduler.runJobInterval, runJob, [scheduler])
        runTimer.daemon = True
        runTimer.start()

#################################################################
# Scheduler                                                     #
#################################################################

# super simple scheduler to run Spark jobs in background
class Scheduler(object):
    def __init__(self, settings, poolSize=5):
        if type(poolSize) is not IntType:
            raise StandardError("Expected IntType, got " + str(type(poolSize)))
        # pull Redis settings and Spark settings
        if "SPARK_UI_ADDRESS" not in settings:
            raise StandardError("Spark UI Address must be specified")
        self.sparkurl = settings["SPARK_UI_ADDRESS"]
        # make connection to Redis
        if "REDIS_HOST" not in settings or "REDIS_PORT" not in settings \
            or "REDIS_DB" not in settings:
            raise StandardError("Redis host, port and db must be specified")
        pool = RedisConnectionPool({
            "host": settings["REDIS_HOST"],
            "port": int(settings["REDIS_PORT"]),
            "db": int(settings["REDIS_DB"])
        })
        connector = RedisConnector(pool)
        self.storageManager = StorageManager(connector)
        # scheduler pool size and queue
        self.poolSize = poolSize
        self.pool = PriorityQueue(poolSize)
        # keep track of jobs processed
        self.jobids = set()
        # interval in seconds to fetch data from storage
        self.fetchInterval = 59.0
        # run job interval in seconds
        self.runJobInterval = 27.0
        # whether timers are running
        self.isRunning = False

    @private
    def fetchStatus(self, status, numJobs):
        return self.storageManager.jobsForStatus(status, limit=numJobs,
            sort=True, reverse=False, sortPriority=True)

    @private
    def hasNext(self):
        return not self.pool.empty()

    @private
    def isFull(self):
        return self.pool.full()

    def add(self, job, priority=100):
        if type(job) is not Job:
            raise StandardError("Expected Job, got " + str(type(job)))
        if type(priority) is not IntType or priority < 0:
            raise StandardError("Priority should be positive integer, got " + str(priority))
        if not self.isFull():
            if job.status != "WAITING":
                self.storageManager.unregisterJob(job, save=False)
                job.updateStatus("WAITING")
                self.storageManager.registerJob(job)
            # we do not add job if it has been added before
            if job.uid not in self.jobids:
                self.pool.put_nowait((priority, job))
                self.jobids.add(job.uid)

    def get(self):
        if self.hasNext():
            tpl = self.pool.get_nowait()
            return tpl[1]
        return None

    # run function that starts fetching and job execution
    def run(self):
        if not self.isRunning:
            self.isRunning = True
            fetch(self)
            runJob(self)
        else:
            print "[WARN] Scheduler is already running"

    # stops timers and scheduler
    def stop(self):
        self.isRunning = False
        print "[INFO] Scheduler is stopped"
