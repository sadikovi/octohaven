#!/usr/bin/env python

import os, json
from Queue import PriorityQueue
from threading import Timer, Lock
from subprocess import Popen, PIPE
from paths import LOGS_PATH
from octolog import Octolog
from job import *
# import job manager to use its keyspace for fetching jobs
from jobmanager import JobManager as provider
from redisconnector import RedisConnector, RedisConnectionPool
from storagemanager import StorageManager
from sparkmodule import SparkModule, DOWN
from utils import *

# create lock, it is unnecessary, because of GIL, but it is safe to have it anyway.
lock = Lock()

# Link class to keep reference for both process and job
class Link(object):
    def __init__(self, jobid, processid=None, uid=None):
        self.uid = uid if uid else "link_%s" % jobid
        self.jobid = jobid
        self.processid = processid

    def isSubmitted(self):
        return bool(self.processid)

    def toDict(self):
        return {"uid": self.uid, "jobid": self.jobid, "processid": self.processid}

    @classmethod
    def fromDict(cls, obj):
        uid = obj["uid"] if "uid" in obj else None
        return cls(obj["jobid"], obj["processid"], uid)

    @staticmethod
    def isLink(obj):
        return True if type(obj) is Link else False

    @staticmethod
    def validateLink(obj):
        if not Link.isLink(obj):
            raise StandardError("Expected Link, got " + str(type(obj)))
        return obj

#################################################################
# Scheduler                                                     #
#################################################################

# timer thread for fetching jobs
fetchTimer = None
# timer thread for running jobs
runTimer = None

def fetch(scheduler):
    try:
        lock.acquire()
        scheduler.logger().info("Starting to fetch jobs that are ready to run...")
        # Calculate min and max boundaries for checking delayed job
        maxT = currentTimeMillis() + scheduler.fetchInterval
        # Check DELAYED jobs. We check them every time, because we do not want to miss window
        delayed = scheduler.jobsForStatus(DELAYED, scheduler.poolSize)
        scheduler.logger().info("Fetched %s DELAYED jobs from storage", len(delayed))
        if len(delayed) > 0:
            # Update status on waiting and priority, so we ensure that delayed job runs first
            for job in delayed:
                if job and job.submittime <= maxT:
                    # delayed job should have higher priority on execution, by order of magnitude
                    # assuming that priority is a submittime. By dividing by 10, we achieve the
                    # same scale of priorities within delayed jobs, but different from waiting and
                    # created jobs
                    scheduler.updateJob(job, WAITING, job.priority / 10)
                    scheduler.logger().info("Updated job %s to run as soon as possible", job.uid)
        # Fetches WAITING jobs first, sorting them by priority, then CREATED, if we have free slots.
        # If there is a delayed job that was updated as waiting, it will be queued and run as fast
        # as possible. If pool is full, then we will have to wait for the next free slot.
        numJobs = scheduler.poolSize - scheduler.pool.qsize()
        if numJobs > 0:
            arr = scheduler.jobsForStatus(WAITING, numJobs)
            scheduler.logger().info("Fetched %s WAITING jobs from storage", len(arr))
            if len(arr) < numJobs:
                numJobs = numJobs - len(arr)
                add = scheduler.jobsForStatus(CREATED, numJobs)
                scheduler.logger().info("Fetched %s CREATED jobs from storage", len(add))
                arr = arr + add
            for job in arr:
                if job.status != WAITING:
                    scheduler.updateJob(job, WAITING, job.priority)
                    scheduler.logger().info("Updated job %s on WAITING from %s", job.uid, job.status)
                scheduler.add(job, job.priority)
        else:
            scheduler.logger().info("Scheduler pool is full, no new jobs were added")
        scheduler.logger().info("Refreshed queue size: %s", scheduler.pool.qsize())
    finally:
        lock.release()
        # Create timer for a subsequent lookup
        fetchTimer = Timer(scheduler.fetchInterval, fetch, [scheduler])
        fetchTimer.daemon = True
        fetchTimer.start()

# Run job method, uses "freshRun" option to indicate whether scheduler runs this method for the
# first time just after being launched
def runJob(scheduler, freshRun=False):
    try:
        lock.acquire()
        # as a first step, update currently running jobs, and handle some error-like situations
        # use simple accumulator to find out how many jobs are actually running
        runningJobs, numRunningJobs = scheduler.jobsForStatus(RUNNING, -1), 0
        for job in runningJobs:
            link = scheduler.linkForUid(Link(job.uid).uid)
            if not link:
                scheduler.logger("No link found for running job %s. Closing it...", job.uid)
                scheduler.updateJob(job, CLOSED, job.priority)
            elif link and not link.isSubmitted():
                scheduler.logger("Job %s does not have assigned process. Closing it...", job.uid)
                scheduler.updateJob(job, CLOSED, job.priority)
            else:
                process = link.processid
                exitcode = scheduler.updateProcessStatus(process)
                if exitcode < 0:
                    scheduler.logger().info("Process %s is still running", process)
                    numRunningJobs += 1
                    # also update finish time to be current time, since it is still running
                    # assess performance, if this is very slow, remove this part
                    job.updateFinishTime(currentTimeMillis())
                    scheduler.updateJob(job, job.status, job.priority)
                else:
                    # finish job by settings status FINISHED and updating finish time
                    # update time to unknown, if scheduler is running method for the first time
                    finishtime = FINISH_TIME_UNKNOWN if freshRun else currentTimeMillis()
                    job.updateFinishTime(finishtime)
                    scheduler.updateJob(job, FINISHED, job.priority)
                    scheduler.removeLink(link)
                    scheduler.logger().info("Process %s finished", process)
        # next step is identifying whether we need to launch a new job
        # we check our pool first, thus, if we do not have jobs to run,
        # do not even bother calling Spark API
        numFreeSlots = scheduler.maxRunningJobs - numRunningJobs
        if numFreeSlots <= 0:
            scheduler.logger().info("Skip launching jobs due to max number of jobs running")
        else:
            scheduler.logger().info("Number of free slots to run: %s", numFreeSlots)
            if not scheduler.hasNext():
                scheduler.logger().info("There are no jobs available in scheduler pool")
                return
            # Check actual Spark running jobs
            runningApps = scheduler.sparkModule.clusterRunningApps()
            if runningApps is None:
                scheduler.logger().warn("Spark cluster is down. Next time then...")
                return
            if len(runningApps) >= scheduler.maxRunningJobs:
                scheduler.logger().info("Max running apps on cluster is reached. Skipping...")
                return
            # we can run jobs, launch `numFreeSlots` jobs
            while numFreeSlots > 0:
                numFreeSlots = numFreeSlots - 1
                while scheduler.hasNext():
                    link = scheduler.nextLink()
                    # refresh status of the job
                    job = scheduler.jobForUid(link.jobid)
                    if not job or job.status != WAITING:
                        scheduler.logger().warn("Cannot resolve job. Fetching next, if available")
                        job = None
                    else:
                        scheduler.logger().info("Running job %s", job.uid)
                        # update actual start time of the job
                        job.updateStartTime(currentTimeMillis())
                        scheduler.updateJob(job, RUNNING, job.priority)
                        link.processid = scheduler.executeSparkJob(job)
                        scheduler.updateLink(link)
                        scheduler.logger().info("Link is saved: %s", link.toDict())
                        break
    except Exception as e:
        scheduler.logger().exception("Runner failed: %s" % e.message)
    finally:
        lock.release()
        # prepare timer for a subsequent operation
        runTimer = Timer(scheduler.runJobInterval, runJob, [scheduler, False])
        runTimer.daemon = True
        runTimer.start()

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
        self.runJobInterval = 7.0
        # maximal number of jobs allowed to run simultaneously
        self.maxRunningJobs = 1
        # whether timers are running
        self.isRunning = False
        # force new Spark master address. If true, it will update master address for a staled job
        # to the valid address specified in configuration file before launching it, e.g. job was
        # saved with address "spark://address1:7077", address was updated to "spark://update:7077",
        # job will be executed with new address, if option is true.
        self.forceSparkMasterAddress = settings["FORCE_SPARK_MASTER_ADDRESS"] if \
            "FORCE_SPARK_MASTER_ADDRESS" in settings else False

    @private
    def hasNext(self):
        return not self.pool.empty()

    @private
    def isFull(self):
        return self.pool.full()

    ############################################################
    ### Scheduler API
    ############################################################
    # fetch jobs sorting them by submittime
    def jobsForStatus(self, status, limit):
        def cmpFunc(x, y):
            return cmp(x.submittime, y.submittime)
        keyspace = provider.keyspace(status)
        return self.storageManager.itemsForKeyspace(keyspace, limit, cmpFunc, Job)

    def jobForUid(self, uid):
        return self.storageManager.itemForUid(uid, klass=Job)

    def updateJob(self, job, newStatus, newPriority):
        self.storageManager.removeItemFromKeyspace(provider.keyspace(job.status), job.uid)
        # update status and priority as we want delayed jobs to run on time
        job.updateStatus(newStatus)
        job.updatePriority(newPriority)
        # resave job and update link
        self.storageManager.saveItem(job, Job)
        self.storageManager.addItemToKeyspace(provider.keyspace(newStatus), job.uid)

    # update only job, assuming that all object properties have been updated
    def updateJobOnly(self, job):
        self.storageManager.saveItem(job, Job)

    def linkForUid(self, uid):
        return self.storageManager.itemForUid(uid, klass=Link)

    def updateLink(self, link):
        self.storageManager.saveItem(link, klass=Link)

    def nextLink(self):
        if not self.hasNext():
            return None
        tpl = self.pool.get_nowait()
        return tpl[1]

    def removeLink(self, link):
        Link.validateLink(link)
        self.storageManager.removeKeyspace(link.uid)

    # add job to the pool by creating a link
    # it is a generic method - we do not check job status
    def add(self, job, priority):
        JobCheck.validateJob(job)
        JobCheck.validatePriority(priority)
        if self.isFull():
            self.logger().info("Could not add job %s. Queue is full", job.uid)
            return False
        # otherwise create a link for that job, and check whether that link exists
        link = Link(job.uid)
        dblink = self.linkForUid(link.uid)
        # it is an odd case when we try adding job, that has already been queued and submitted
        if dblink and dblink.isSubmitted():
            self.logger().error("Attempt to resubmit the job. Link dump: %s. Job dump: %s",
                dblink.toDict(), job.toDict())
            return False
        # case when job is already added to queue, thus we do not want to add it again.
        if dblink and not dblink.isSubmitted():
            if not self.hasNext():
                self.logger().error("Tried skipping job while pool is empty. Recovering...")
                self.removeLink(dblink)
            else:
                self.logger().info("Skip job with uid %s and priority %s as it is already in " + \
                    "the queue", job.uid, priority)
            return False
        # once we are here, we know that there is no link currently, therefore we safely queue job
        self.storageManager.saveItem(link, klass=Link)
        self.pool.put_nowait((priority, link))
        self.logger().info("Add job with uid %s, status %s, priority %s", job.uid, job.status,
            priority)

    # check process status, returns:
    # 2: process exited with critical error
    # 1: process exited with error
    # 0: process successfully finished
    # -1: process is still running
    def updateProcessStatus(self, pid):
        if not pid:
            return 2
        # replaced command to check process to fetch exact pid
        cmd = ["ps", "-p", str(pid), "-o", "pid=", "-o", "user=", "-o", "ppid=", "-o", "args="]
        p1 = Popen(cmd, stdout=PIPE)
        output = p1.communicate()[0]
        # process is still running
        if output and len(output) > 0:
            return -1
        # otherwise we always return 0 for now
        return 0

    # execute Spark job commmand in NO_WAIT mode.
    # Also specify stdout and stderr folders for a job
    # Returns process id for a job
    def executeSparkJob(self, job):
        if self.forceSparkMasterAddress:
            # check if Spark master address is different from saved job address
            sparkJob = job.getSparkJob()
            if sparkJob.getMasterUrl() != self.sparkModule.masterAddress:
                self.logger().warning("Job master url %s will be updated to new master url %s",
                    sparkJob.getMasterUrl(), self.sparkModule.masterAddress)
                sparkJob.updateMasterUrl(self.sparkModule.masterAddress)
                # update job in storage
                self.updateJobOnly(job)
        # get execute command
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
                f.write(json.dumps(job.toDict()))
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

    ############################################################
    ### Scheduler main methods
    ############################################################
    # run function that starts fetching and job execution
    def run(self):
        if self.isRunning:
            self.stop()
        self.logger().info("Scheduler is running")
        self.isRunning = True
        fetch(self)
        # set fresh run to True, so we can update running jobs properly
        runJob(self, freshRun=True)

    # stop timers and scheduler
    def stop(self):
        self.isRunning = False
        self.logger().info("Scheduler is stopped")
