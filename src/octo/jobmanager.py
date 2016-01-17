#!/usr/bin/env python

import re, shlex, src.octo.utils as utils
from src.octo.mysqlcontext import MySQLContext
from src.octo.storagemanager import StorageManager
from types import DictType, StringType, IntType
from job import Job, READY, DELAYED, CLOSED, RUNNING, FINISHED, CLOSABLE_STATUSES
from sparkjob import SparkJob

JOB_DEFAULT_NAME = "Another octojob"

# Job manager is responsible for creating and managing Job and SparkJob instances, though it is not
# responsible for scheduling jobs
class JobManager(object):
    def __init__(self, storageManager):
        utils.assertInstance(storageManager, StorageManager)
        self.storage = storageManager

    # Parse Spark conf options. We process only "--conf" options ignoring everything else.
    # Probably, should be extended to parse all the Spark command-line arguments.
    @utils.private
    def parseOptions(self, options):
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
            raise StandardError("Cannot process options of type %s" % type(options))
        return updatedOptions

    # Parse job (not Spark) options that go after .jar file to feed into main function of entrypoint
    @utils.private
    def parseJobConf(self, jobconf):
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
            raise StandardError("Cannot process job conf options of type %s" % type(jobconf))
        return updatedJobConf

    # Create new Job and SparkJob instances
    # - name => a friendly name of a job
    # - delay => an offset in seconds to run job after some time
    # - entrypoint => a main class of the jar file
    # - jar => a path to the jar file
    # - driverMemory => a amount of driver memory for the job
    # - executorMemory => an amount of executor memory for the job
    # - opts => additional Spark options
    # - jobconf => additional specific job (not Spark) options
    def createJob(self, name, delay, entrypoint, jar, driverMemory, executorMemory, opts, jobconf):
        # validate name
        name = JOB_DEFAULT_NAME if not str(name).strip() else str(name).strip()
        # validate delay of the job
        utils.assertInstance(delay, IntType, "Delay type %s is not IntType" % type(delay))
        # update status based on delay
        status = READY if delay <= 0 else DELAYED
        # store start time as unix timestamp in ms
        createtime = utils.currentTimeMillis()
        # reevaluate submit time considering delay
        submittime = createtime if delay <= 0 else (createtime + delay * 1000L)
        # parse options correctly, job accepts already parsed options as
        # key-value pairs, e.g. spark.shuffle.spill=true
        # we do not fail, if there are no options
        updatedOptions = self.parseOptions(opts)
        # we also parse job configuration options, the same principle really
        updatedJobConf = self.parseJobConf(jobconf)
        # add driver and executor memory, because we specify them as completely separate options
        # we also override any other config options for executor / driver memory
        updatedOptions["spark.driver.memory"] = driverMemory
        updatedOptions["spark.executor.memory"] = executorMemory

        # build dummy dictionaries without ids, store content, update uid and return Job
        # store Spark job, get uid => update Job => store Job => get uid
        sparkDict = SparkJob(None, name, entrypoint, jar, updatedOptions, updatedJobConf).dict()
        jobDict = Job(None, name, status, createtime, submittime, None).dict()
        jobDict["uid"] = self.storage.createJob(sparkDict, jobDict)
        return Job.fromDict(jobDict)

    # Close job safely, checks whether status can be changed on CLOSED
    def closeJob(self, job):
        utils.assertInstance(job, Job)
        if job.status not in CLOSABLE_STATUSES:
            raise StandardError("Cannot close job with status %s" % job.status)
        self.storage.updateStatus(job.uid, CLOSED)
        job.updateStatus(CLOSED)

    # Extract job with Spark job data. Return tuple where first element is job instance and second
    # element is SparkJob instance
    def jobForUid(self, uid, withSparkJob=True):
        data = self.storage.getJob(uid, withSparkJob=True)
        if not data:
            return (None, None)
        # parse data into 2 separate dictionaries
        jdict, sdict = {}, {}
        for key, value in data.items():
            if key.startswith("spark_"):
                sdict[key.replace("spark_", "")] = value
            else:
                jdict[key] = value
        job = Job.fromDict(jdict)
        sparkjob = SparkJob.fromDict(sdict) if withSparkJob else None
        return (job, sparkjob)

    # Return list of jobs with any status with limit
    def jobs(self, limit=50):
        rows = self.storage.getJobsByCreateTime(limit, desc=True)
        return map(lambda row: Job.fromDict(row), rows) if rows else []

    # Return list of jobs for a particular status with limit and sort
    def jobsForStatus(self, status, limit=50):
        Job.checkStatus(status)
        rows = self.storage.getJobsByStatusCreateTime(status, limit, desc=True)
        return map(lambda row: Job.fromDict(row), rows) if rows else []

    ############################################################
    # Scheduler-specific API
    ############################################################
    # Update status to finish job properly (update status and finish time)
    def finishJob(self, job):
        utils.assertInstance(job, Job)
        if job.status is not RUNNING:
            raise StandardError("Cannot finish job with status %s" % job.status)
        now = utils.currentTimeMillis()
        self.storage.updateStatusAndFinishTime(job.uid, FINISHED, now)
        job.updateStatus(FINISHED)
        job.updateFinishTime(now)
