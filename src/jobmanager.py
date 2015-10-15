#!/usr/bin/env python

import paths
import uuid, re, time
from job import Job, JobCheck, SparkJob
from types import DictType, StringType
from utils import *

# purpose of job manager is providing simple interface of creating job as a result
# of request / loading from storage. It is not responsible for scheduling jobs though.
class JobManager(object):
    def __init__(self, masterurl):
        self.masterurl = JobCheck.validateMasterUrl(masterurl)

    @private
    def parseOptions(self, options):
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

    # method is also called in theserver.py to create separate Spark job
    def createSparkJob(self, name, entrypoint, jar, driverMemory, executorMemory, options):
        # parse options correctly, job accepts already parsed options as
        # key-value pairs, e.g. spark.shuffle.spill=true
        # we do not fail, if there are no options
        uid = "spark_" + uuid.uuid4().hex
        updatedOptions = self.parseOptions(options)
        # add driver and executor memory, because we specify them as completely separate options
        # we also override any other config options for executor / driver memory
        updatedOptions["spark.driver.memory"] = driverMemory
        updatedOptions["spark.executor.memory"] = executorMemory
        return SparkJob(uid, name, self.masterurl, entrypoint, jar, updatedOptions)

    # creates Job instance, fails if anything is wrong with a job.
    def createJob(self, sparkjob):
        uid = "job_" + uuid.uuid4().hex
        status = "CREATED"
        duration = "MEDIUM"
        # store start time as unix timestamp in ms
        submittime = long(time.time() * 1000)
        return Job(uid, status, submittime, duration, sparkjob)
