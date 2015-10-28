#!/usr/bin/env python

import os, time
from Queue import PriorityQueue
from types import IntType
from threading import Timer, Lock
from subprocess import Popen, PIPE
from paths import LOGS_PATH
from octolog import Octolog
from job import *
from redisconnector import RedisConnector, RedisConnectionPool
from storagemanager import StorageManager
from sparkmodule import SparkModule, DOWN
from utils import *


SCHEDULER_UID_PREFIX = "scheduler_prefix"
SCHEDULER_RUN_POOL = "scheduler_run_pool"
# create lock, it is unnecessary, because of GIL, but it is safe to have it anyway.
lock = Lock()

# Link class to keep reference for both process and job
class Link(object):
    def __init__(self, processid, jobid):
        self.uid = processid
        self.processid = processid
        self.jobid = jobid

    def toDict(self):
        return {"uid": self.uid, "processid": self.processid, "jobid": self.jobid}

    @classmethod
    def fromDict(cls, obj):
        processid = obj["processid"]
        jobid = obj["jobid"]
        return cls(processid, jobid)

# method populates queue with fresh jobs with statuses WAITING and CREATED
def fetch(scheduler):
    try:
        lock.acquire()
        # current time in milliseconds
        currTime = long(time.time() * 1000)
        # calculate min and max boundaries for checking delayed job
        minT, maxT = currTime - scheduler.fetchInterval/10, currTime + scheduler.fetchInterval
        # Pre-step of checking DELAYED jobs. We need to check them every time, fetch runs, because
        # we do not want to miss the window
        scheduler.logger().info("Checking DELAYED jobs")
        delayed = scheduler.fetchStatus(DELAYED, scheduler.poolSize)
        scheduler.logger().info("Fetched %s DELAYED jobs", len(delayed))
        if len(delayed) > 0:
            # update status on waiting and priority
            # in this case we also fetch jobs that were overdue and not necessary need to be run.
            due = [j for j in delayed if j and j.submittime <= maxT]
            for dueJob in due:
                scheduler.updateJob(dueJob, WAITING, dueJob.priority - 1)
                scheduler.logger().info("Updated job %s to run as soon as possible", dueJob.uid)
        # proper scheduling fetch
        # fetches WAITING jobs first, sorting them by priority, then CREATED, if we have free slots.
        # if there is a delayed job that was updated as waiting, it will be queued and run as fast
        # as possible. If pool is full, then we will have to wait for the next free slot.
        numJobs = scheduler.poolSize - scheduler.pool.qsize()
        if numJobs > 0:
            scheduler.logger().info("Requested %s jobs from storage", numJobs)
            arr = scheduler.fetchStatus(WAITING, numJobs)
            scheduler.logger().info("Fetched %s WAITING jobs from storage", len(arr))
            if len(arr) < numJobs:
                # we have to check created jobs
                numJobs = numJobs - len(arr)
                add = scheduler.fetchStatus(CREATED, numJobs)
                scheduler.logger().info("Fetched %s CREATED jobs from storage", len(add))
                arr = arr + add
            for job in arr:
                if job.status != WAITING:
                    scheduler.updateJob(job, WAITING, job.priority)
                    scheduler.logger().info("Updated job %s on WAITING from %s", job.uid, job.status)
                scheduler.add(job, job.priority)
        else:
            scheduler.logger().info("No new jobs were added")
        scheduler.logger().info("Updated queue size: %s", scheduler.pool.qsize())
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
        storage = scheduler.storageManager
        # Check every process status available of jobs running, if any
        links = storage.itemsForKeyspace(SCHEDULER_RUN_POOL, limit=-1, cmpFunc=None, klass=Link)
        for link in links:
            if type(link) is not Link:
                scheduler.logger().error("Could not resolve process link for %s", str(link))
                storage.removeKeyspace(SCHEDULER_RUN_POOL)
                # as we removed all the links to the process, we close jobs that were running
                scheduler.logger().info("Cleaning broken process links")
                runningJobs = storage.itemsForKeyspace(RUNNING, -1, None, Job)
                for job in runningJobs:
                    scheduler.updateJob(job, CLOSED, job.priority)
                    scheduler.logger().info("Closed job %s, because of a broken link", job.uid)
                raise StandardError("Could not resolve process link for %s" % str(link))
            # Update job, if its status has changed: set status FINISHED and remove link
            processid = link.processid
            # refresh status
            exitcode = scheduler.updateProcessStatus(processid)
            if exitcode < 0:
                scheduler.logger().info("Process %s is still running", processid)
            else:
                # process is finished, we need to update job
                scheduler.logger().info("Process %s finished", processid)
                jobid = link.jobid
                job = scheduler.storageManager.itemForUid(jobid, klass=Job)
                if job:
                    scheduler.updateJob(job, FINISHED, job.priority)
                else:
                    scheduler.logger().warning("Job was not found for uid %s, skip update", jobid)
                # remove process
                scheduler.storageManager.removeItemFromKeyspace(SCHEDULER_RUN_POOL, processid)
        # Check whether we need a new job, pull all data again, since we might have found links
        links = storage.itemsForKeyspace(SCHEDULER_RUN_POOL, -1, None, Link)
        numFreeSlots = scheduler.maxRunningJobs - len(links)
        if numFreeSlots > 0:
            scheduler.logger().info("Number of free slots: %s", numFreeSlots)
            # Check server running apps, if we can actually run a job.
            runningApps = scheduler.sparkModule.clusterRunningApps()
            if runningApps is None:
                scheduler.logger().info("Spark cluster is down. Next time then...")
            elif len(runningApps) >= scheduler.maxRunningJobs:
                scheduler.logger().info("Max running apps on cluster is reached. Skipping...")
            else:
                # Change status on running and execute command for a job
                while numFreeSlots > 0:
                    numFreeSlots = numFreeSlots - 1
                    job = None
                    while scheduler.hasNext() and not job:
                        job = scheduler.get()
                        # refresh status of the job
                        verify = storage.itemForUid(job.uid, klass=Job)
                        if not verify or verify.status != job.status:
                            scheduler.logger().error("Could not resolve job. Fetching next")
                            job = None
                            continue
                    if not job:
                        scheduler.logger().info("There are no jobs available in scheduler pool")
                    else:
                        scheduler.logger().info("Submitting the job %s", job.uid)
                        scheduler.updateJob(job, RUNNING, job.priority)
                        # run command with NO_WAIT
                        processid = scheduler.executeSparkJob(job)
                        # Add link "process id - job id"
                        link = Link(processid, job.uid)
                        storage.saveItem(link, klass=Link)
                        storage.addItemToKeyspace(SCHEDULER_RUN_POOL, processid)
                        scheduler.logger().info("Link is saved %s - %s", processid, job.uid)
    except BaseException as e:
        scheduler.logger().exception("Runner failed: %s" % e.message)
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
class Scheduler(Octolog, object):
    def __init__(self, settings, poolSize=5):
        if type(poolSize) is not IntType:
            raise StandardError("Expected IntType, got " + str(type(poolSize)))
        # pull Spark settings
        if "SPARK_UI_ADDRESS" not in settings:
            raise StandardError("Spark UI Address is not specified")
        if "SPARK_UI_RUN_ADDRESS" not in settings:
            raise StandardError("Spark UI Address for running applications is not specified")
        if "SPARK_MASTER_ADDRESS" not in settings:
            raise StandardError("Spark Master Address is not specified")
        sparkUi = settings["SPARK_UI_ADDRESS"]
        sparkUiRun = settings["SPARK_UI_RUN_ADDRESS"]
        sparkMaster = settings["SPARK_MASTER_ADDRESS"]
        # make connection to Redis
        if "REDIS_HOST" not in settings:
            raise StandardError("Redis host is not specified")
        if "REDIS_PORT" not in settings:
            raise StandardError("Redis port is not specified")
        if "REDIS_DB" not in settings:
            raise StandardError("Redis db is not specified")
        pool = RedisConnectionPool({
            "host": settings["REDIS_HOST"],
            "port": int(settings["REDIS_PORT"]),
            "db": int(settings["REDIS_DB"])
        })
        connector = RedisConnector(pool)
        self.storageManager = StorageManager(connector)
        self.sparkModule = SparkModule(sparkMaster, sparkUi, sparkUiRun)
        # scheduler pool size and queue
        self.poolSize = poolSize
        self.pool = PriorityQueue(poolSize)
        # interval in seconds to fetch data from storage
        self.fetchInterval = 11.0
        # run job interval in seconds
        self.runJobInterval = 5.0
        # maximal number of jobs allowed to run simultaneously
        self.maxRunningJobs = 1
        # whether timers are running
        self.isRunning = False

    @private
    def fetchStatus(self, status, numJobs):
        def cmpFunc(x, y):
            return cmp(x.submittime, y.submittime)
        return self.storageManager.itemsForKeyspace(status, numJobs, cmpFunc, Job)

    @private
    def hasNext(self):
        return not self.pool.empty()

    @private
    def isFull(self):
        return self.pool.full()

    # add job to the pool, we do not check job status
    def add(self, job, priority):
        JobCheck.validateJob(job)
        JobCheck.validatePriority(priority)
        if not self.isFull():
            uid = "%s-%s" % (SCHEDULER_UID_PREFIX, job.uid)
            # we do not add job if it has been added before
            if not self.storageManager.itemForUid(uid):
                self.pool.put_nowait((priority, job))
                self.storageManager.saveItem({"uid": uid})
                self.logger().info("Add job with uid %s and priority %s" % (job.uid, priority))
            else:
                self.logger().info("Skip job with uid %s and priority %s" % (job.uid, priority))
                if not self.hasNext():
                    self.logger().error("Tried skipping job while pool is empty. Recovering...")
                    self.storageManager.removeKeyspace(uid)

    def updateJob(self, job, newStatus, newPriority):
        self.storageManager.removeItemFromKeyspace(job.status, job.uid)
        # update status and priority as we want delayed jobs to run on time
        job.updateStatus(newStatus)
        job.updatePriority(newPriority)
        # resave job and update link
        self.storageManager.saveItem(job, Job)
        self.storageManager.addItemToKeyspace(newStatus, job.uid)

    # check process status, returns:
    # 2: process exited with critical error
    # 1: process exited with error
    # 0: process successfully finished
    # -1: process is still running
    def updateProcessStatus(self, processid):
        if not processid:
            return 2
        p1 = Popen(["ps", "aux"], stdout=PIPE)
        p2 = Popen(["grep", "-i", str(processid)], stdin=p1.stdout, stdout=PIPE)
        p1.stdout.close()
        p3 = Popen(["grep", "-i", "spark"], stdin=p2.stdout, stdout=PIPE)
        p2.stdout.close()
        output = p3.communicate()[0]
        # process is still running
        if output and len(output) > 0:
            return -1
        # otherwise we always return 0 for now
        return 0

    # execute Spark job commmand in NO_WAIT mode.
    # Also specify stdout and stderr folders for a job
    # Returns process id for a job
    def executeSparkJob(self, job):
        cmd = job.execCommand()
        self.logger().info("Executing command: %s", str(cmd))
        # open output and error files in folder specific for that jobid
        out, err = None, None
        try:
            # make directory for the Spark job
            jobDir = os.path.join(LOGS_PATH, str(job.uid))
            os.makedirs(jobDir)
            # create metadata file with job settings
            metadataPath = os.path.join(jobDir, "_metadata")
            with open(metadataPath, 'wb') as f:
                f.write(str(job.toDict()))
            # create files
            outPath = os.path.join(jobDir, "stdout")
            errPath = os.path.join(jobDir, "stderr")
            out = open(outPath, "wb")
            err = open(errPath, "wb")
        except:
            self.logger().exception("Error happened during creation of stdout and stderr for " + \
                "job id %s. Using default None values" % job.uid)
            out = None
            err = None
        # run process
        processid = Popen(cmd, stdout=out, stderr=err, close_fds=True).pid
        return processid

    def get(self):
        if not self.hasNext():
            return None
        tpl = self.pool.get_nowait()
        return tpl[1]

    # run function that starts fetching and job execution
    def run(self):
        if self.isRunning:
            self.logger().warning("Scheduler is already running")
        self.logger().info("Scheduler is running")
        self.isRunning = True
        fetch(self)
        runJob(self)

    # stops timers and scheduler
    def stop(self):
        self.isRunning = False
        self.logger().info("Scheduler is stopped")
