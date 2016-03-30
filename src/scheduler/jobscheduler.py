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
from src.octohaven import db, workingDirectory

scheduler = Loggable("job-scheduler")

# Constants for folders and files created
METADATA = "_metadata"
STDOUT = "stdout"
STDERR = "stderr"

# Build full absolute path to the job working directory
def jobWorkingDirectory(uid):
    return os.path.join(workingDirectory, "job-%s" % uid)

# Execute Spark job commmand in NO_WAIT mode.
# Also specify stdout and stderr folders for a job
# Returns process id for a job
@utils.private
def launchSparkJob(job):
    cmd = job.execCommand()
    scheduler.logger().info("Launching command: %s", cmd)
    # open output and error files in folder specific for that jobid
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
        scheduler.logger().exception("Error happened during creation of stdout and stderr for " + \
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

# Generic start function, registers/cleans up jobs and adds them to the pool
def start():
    pass

# Generic stop function, performs clean up of the pool and cancelling jobs in progress
def stop():
    pass
