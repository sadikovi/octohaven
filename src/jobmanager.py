#!/usr/bin/env python

import paths
import uuid, re, time, shlex
from types import DictType, StringType, IntType
from job import *
from storagemanager import StorageManager
from sparkmodule import SparkModule
from utils import *

# key to store history of all the jobs in the system
ALL_JOBS_KEY = "ALL"

# purpose of job manager is providing simple interface of creating job as a result
# of request / loading from storage. It is not responsible for scheduling jobs though.
# takes SparkModule and StorageManager as parameters to provide unified interface.
class JobManager(object):
    def __init__(self, sparkModule, storageManager):
        if type(sparkModule) is not SparkModule:
            raise StandardError("Expected SparkModule, got " + str(type(sparkModule)))
        if type(storageManager) is not StorageManager:
            raise StandardError("Expected StorageManager, got " + str(type(storageManager)))
        self.sparkModule = sparkModule
        self.storageManager = storageManager


    @private
    def parseOptions(self, options):
        # parses Spark conf options
        # we process only "--conf" options ignoring everything else.
        # probably, should be extended to parse all the Spark command-line arguments.
        updatedOptions = {}
        if type(options) is StringType:
            # parse string into options
            for pair in options.strip().split("--conf"):
                pair = pair.strip()
                pattern = "&"
                # we use different patterns for quoted and unqouted options
                # could be done other way, using buffer or some complex regex
                if pair.startswith("\""):
                    pattern = r"\"(\w+\.\w+\.\w+)\s*=\s*([^\"]+)\""
                else:
                    pattern = r"(\w+\.\w+\.\w+)\s*=\s*([\S]+)"
                groups = re.match(pattern, pair)
                if groups:
                    updatedOptions[groups.group(1)] = groups.group(2)
        elif type(options) is DictType:
            # should, probably, verify that dictionary is correct
            updatedOptions = options
        else:
            raise StandardError("Cannot process options of type " + str(type(options)))
        return updatedOptions

    @private
    def parseJobConf(self, jobconf):
        # parses job (not Spark) options that go after .jar file to feed into main function of
        # entrypoint
        updatedJobConf = []
        if type(jobconf) is StringType:
            # job configuration options are passed as string.
            # we need to tokenize them properly, as close as possible
            # handles empty string as well
            try:
                updatedJobConf = shlex.split(jobconf)
            except SyntaxError:
                raise StandardError("Invalid syntax for the command: %s" % jobconf)
        elif type(jobconf) is ListType:
            # job conf options are passed as list, we assume that they are already prepared to
            # be used in process invocation
            updatedJobConf = jobconf
        else:
            raise StandardError("Cannot process job conf options of type " + str(type(jobconf)))
        return updatedJobConf

    # method is also called in theserver.py to create separate Spark job
    # - name => a friendly name of a job
    # - entrypoint => a main class of the jar file
    # - jar => a path to the jar file
    # - driverMemory => a amount of driver memory for the job
    # - executorMemory => an amount of executor memory for the job
    # - opts => additional Spark options
    # - jobconf => additional specific job (not Spark) options
    def createSparkJob(self, name, entrypoint, jar, driverMemory, executorMemory, opts, jobconf=""):
        # parse options correctly, job accepts already parsed options as
        # key-value pairs, e.g. spark.shuffle.spill=true
        # we do not fail, if there are no options
        uid = "spark_" + uuid.uuid4().hex
        masterurl = self.sparkModule.masterAddress
        updatedOptions = self.parseOptions(opts)
        # we also parse job configuration options, the same principle really
        updatedJobConf = self.parseJobConf(jobconf)
        # add driver and executor memory, because we specify them as completely separate options
        # we also override any other config options for executor / driver memory
        updatedOptions["spark.driver.memory"] = driverMemory
        updatedOptions["spark.executor.memory"] = executorMemory
        return SparkJob(uid, name, masterurl, entrypoint, jar, updatedOptions, updatedJobConf)

    # creates Job instance, fails if anything is wrong with a job.
    # - sparkjob => an instance of SparkJob class
    # - delay => an offset in seconds to run job after some time
    def createJob(self, sparkjob, delay=0):
        if type(delay) is not IntType:
            raise StandardError("Delay is expected to be of IntType, got " + str(type(delay)))
        uid = "job_" + uuid.uuid4().hex
        status = CREATED if delay <= 0 else DELAYED
        duration = MEDIUM
        # store start time as unix timestamp in ms
        createtime = long(time.time() * 1000)
        # reevaluate submit time considering delay
        scheduletime = createtime if delay <= 0 else (createtime + delay * 1000)
        return Job(uid, status, createtime, scheduletime, duration, sparkjob)

    # saves job into storage and registers job for a specific + global status
    def saveJob(self, job):
        JobCheck.validateJob(job)
        self.storageManager.saveItem(job, klass=Job)
        self.storageManager.addItemToKeyspace(ALL_JOBS_KEY, job.uid)
        self.storageManager.addItemToKeyspace(job.status, job.uid)

    # change job status to any arbitrary allowed status
    # - job => job to change status for
    # - newStatus => new status to update
    # - validationRule => validation rule between old and new statuses, should return boolean
    # - pushToStorage => if True updates data in storage
    def changeStatus(self, job, newStatus, validationRule=None, pushToStorage=True):
        JobCheck.validateJob(job)
        oldStatus = job.status
        if newStatus != oldStatus and validationRule and validationRule(oldStatus, newStatus):
            job.updateStatus(newStatus)
            if pushToStorage:
                self.storageManager.removeItemFromKeyspace(oldStatus, job.uid)
                self.storageManager.saveItem(job, klass=Job)
                self.storageManager.addItemToKeyspace(newStatus, job.uid)

    # closes job safely, checks whether status can be changed on CLOSED
    def closeJob(self, job):
        def validate(oldStatus, newStatus):
            if oldStatus not in CAN_CLOSE_STATUSES:
                raise StandardError("Cannot close job with a status %s" % oldStatus)
            return True
        self.changeStatus(job, CLOSED, validate, True)

    # simple wrapper for job extraction by id
    def jobForUid(self, uid):
        return self.storageManager.itemForUid(uid, klass=Job)

    # simple wrapper around `jobsForStatus` method of StorageManager
    def listJobsForStatus(self, status, limit, sort):
        def sortFunc(x, y):
            return -1 * cmp(x.createtime, y.createtime)
        # status is invalid or does not match global keyspace, raise an error explicitly
        if status.upper() not in STATUSES and status.upper() != ALL_JOBS_KEY:
            raise StandardError("Invalid status " + status + " to fetch")
        limit = limit if type(limit) is IntType else 30
        cmpFunc = sortFunc if sort else None
        return self.storageManager.itemsForKeyspace(status, limit, cmpFunc, klass=Job)
