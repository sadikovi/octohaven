#!/usr/bin/env python

#
# Copyright 2015 sadikovi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import src.utils as utils
from flask import json
from flask.ext.sqlalchemy import SignallingSession
from Queue import PriorityQueue
from threading import Timer, Lock
from subprocess import Popen, PIPE
from src.loggable import Loggable
from src.job import Job
from src.octohaven import db, workingDirectory, sparkContext, numSlots
from src.sparkmodule import DOWN

# Main scheduler object for logging
scheduler = Loggable("job-scheduler")

lock = Lock()
# Number of slots, the maximum number of jobs to run at the same time
NUM_SLOTS = numSlots
# Interval to update current running state and poll jobs in seconds
REFRESH_INTERVAL = 5.0

# Constants for folders and files created
METADATA = "_metadata"
STDOUT = "stdout"
STDERR = "stderr"

@utils.private
def action(sampler):
    if not sampler:
        scheduler.logger.error("Sampler is undefined, exiting")
        return
    session = SignallingSession(db)
    try:
        sampler.logger.info("Start refreshing application state")
        sampler.incrementNumRuns()
        lock.acquire()
        for uid, pid in sampler.pool.items():
            if updateProcessStatus(pid) >= 0:
                job = Job.get(session, uid)
                if not job:
                    sampler.logger.warn("Job '%s' does not exist in database, updated skipped", uid)
                else:
                    Job.finish(session, job)
                sampler.removeFromPool(uid)
            else:
                sampler.logger.info("Process '%s' is still running, job uid: '%s'", pid, uid)
        # Check how many pids are left. Compare against NUM_SLOTS, if comparison yields false,
        # skip execution, otherwise it yields true, and we proceed with number of free slots
        freeSlots = NUM_SLOTS - len(sampler.pool)
        if freeSlots <= 0:
            sampler.logger.info("All %s slots are taken, cannot launch job, skipped", NUM_SLOTS)
            sampler.logger.debug("Free slots: %s, pool size: %s, numSlots: %s", freeSlots,
                len(sampler.pool), NUM_SLOTS)
        else:
            # Check how many jobs are running at the moment by checking status of the cluster and
            # requesting number of running applications, if number of applications is equal or more
            # than NUM_SLOTS, skip execution, otherwise compute number of jobs to launch and proceed.
            sparkStatus = sparkContext.clusterStatus()
            if sparkStatus == DOWN:
                sampler.logger.info("Cluster %s[%s] is down, will try again later",
                    sparkContext.getMasterAddress(), sparkContext.getUiAddress())
            else:
                apps = sparkContext.clusterRunningApps()
                freeSlots = NUM_SLOTS - len(apps)
                if freeSlots <= 0:
                    sampler.logger.info("There are %s applications running already, cannot " + \
                        "launch job, skipped", len(apps))
                    sampler.logger.debug("Free slots: %s, apps: %s, numSlots: %s", freeSlots,
                        len(apps), NUM_SLOTS)
                else:
                    # Fetch jobs active (runnable) jobs using Job API based on number of free slots,
                    # acquired earlier. Start jobs in the list, if any. Report when no jobs found.
                    currentTime = utils.currentTimeMillis()
                    sampler.logger.debug("Fetch jobs with session %s, free slots %s, time %s",
                        session, freeSlots, currentTime)
                    runnableJobs = Job.listRunnable(session, freeSlots, currentTime)
                    sampler.logger.info("Registering %s jobs", len(runnableJobs))
                    for job in runnableJobs:
                        pid = launchSparkJob(job)
                        Job.run(session, job)
                        sampler.addToPool(job.uid, pid)

        session.commit()
    except Exception as e:
        sampler.logger.error("Sampler encountered error, execution skipped")
        sampler.logger.exception(e.message)
    finally:
        lock.release()
        session.close()
        if sampler.enabled:
            sampler.logger.debug("Prepared to be invoked in %s seconds", sampler.interval)
            timer = Timer(sampler.interval, action, [sampler])
            timer.daemon = True
            timer.start()
        else:
            sampler.logger.info("Sampler stopped")

# Sampler keeps track of running pids and polls jobs from the database, there is only one sampler
# at the time.
class Sampler(Loggable, object):
    def __init__(self):
        super(Sampler, self).__init__()
        self.enabled = False
        self.interval = REFRESH_INTERVAL
        self.pool = {}
        self.numRuns = 0

    # Register job uid and pid associated with it
    def addToPool(self, uid, pid):
        if uid in self.pool:
            self.logger.warn("Pool already has '%s' -> '%s', will be overwritten by '%s' -> '%s'",
                uid, self.pool[uid], uid, pid)
        self.pool[uid] = pid
        self.logger.debug("Added '%s' -> '%s' to the pool", uid, pid)

    # Remove job uid from the pool
    def removeFromPool(self, uid):
        if uid not in self.pool:
            self.logger.warn("Could not find uid '%s' in the pool", uid)
        del self.pool[uid]
        self.logger.debug("Removed uid '%s' from the pool", uid)

    def incrementNumRuns(self):
        self.numRuns = self.numRuns + 1

    def start(self):
        if self.enabled:
            self.logger.warn("Sampler is already running, skipped")
            return None
        self.enabled = True
        self.numRuns = 0
        action(self)

    def stop(self):
        self.enabled = False
        for uid in self.pool.keys():
            self.removeFromPool(uid)

# Build full absolute path to the job working directory
def jobWorkingDirectory(uid):
    return os.path.join(workingDirectory, "job-%s" % uid)

# Execute Spark job commmand in NO_WAIT mode.
# Also specify stdout and stderr folders for a job
# Returns process id for a job
@utils.private
def launchSparkJob(job):
    cmd = job.execCommand(sparkContext)
    scheduler.logger.info("Launching command: %s", cmd)
    # Open output and error files in folder specific for that jobid
    out, err = None, None
    try:
        # make directory for the Spark job
        jobDir = jobWorkingDirectory(job.uid)
        os.makedirs(jobDir)
        # create metadata file with job settings
        metadataPath = os.path.join(jobDir, METADATA)
        with open(metadataPath, 'wb') as f:
            f.write(json.dumps(job.json()))
        # create files
        outPath = os.path.join(jobDir, STDOUT)
        errPath = os.path.join(jobDir, STDERR)
        out = open(outPath, "wb")
        err = open(errPath, "wb")
    except:
        scheduler.logger.exception("Error happened during creation of stdout and stderr for " + \
            "job id %s. Using default None values", job.uid)
        out = None
        err = None
    # run process
    pid = Popen(cmd, stdout=out, stderr=err, close_fds=True).pid
    return pid

# Check process status, returns:
# 2: process exited with critical error
# 1: process exited with error
# 0: process successfully finished
# -1: process is still running
@utils.private
def updateProcessStatus(pid):
    if not pid:
        return 2
    # Replaced command to check process to fetch exact pid
    # make sure that pid is spark-submit job, because of a possibility of accessing assigned to
    # other process pid after system restart
    cmd = ["ps", "-p", str(pid), "-o", "pid=", "-o", "user=", "-o", "ppid=", "-o", "args="]
    p1 = Popen(cmd, stdout=PIPE)
    p2 = Popen(["grep", "-i", "sparksubmit"], stdin=p1.stdout, stdout=PIPE)
    p1.stdout.close()
    output = p2.communicate()[0]
    # Process is still running
    if output and len(output) > 0:
        return -1
    # Otherwise we always return 0 for finished process (either killed or finished
    # successfully) for now
    return 0

# Sampler object
sampler = Sampler()

# Generic start function, registers/cleans up jobs and adds them to the pool
def start():
    session = SignallingSession(db)
    session.begin(subtransactions=True)
    # We fetch all jobs for the queue when invoked
    jobs = Job.listRunning(session)
    scheduler.logger.info("Fetched %s jobs to analyze", len(jobs))
    running = [x for x in jobs if x.status == Job.RUNNING]
    for x in running:
        x.status = Job.CLOSED
        session.commit()
        scheduler.logger.info("Running job '%s' is closed, cannot resolve process id", x.uid)
    session.commit()
    session.close()
    # Start sampler
    sampler.start()
    scheduler.logger.info("Job scheduler is started, refresh interval = %s, number of slots = %s",
        REFRESH_INTERVAL, NUM_SLOTS)

# Generic stop function, performs clean up of the pool and cancelling jobs in progress
def stop():
    sampler.stop()
    scheduler.logger.info("Sampler stopped")
    scheduler.logger.info("Job scheduler is stopped")
