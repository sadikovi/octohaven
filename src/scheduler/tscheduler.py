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

import src.utils as utils
from flask.ext.sqlalchemy import SignallingSession
from threading import Timer, Lock
from src.loggable import Loggable
from src.timetable import Timetable
from src.octohaven import db

# Minimal interval in seconds for timetable scheduling.
# It does not make sense keep it less than 1 minute
MINIMAL_INTERVAL = 60.0

# Pool lock for updates
pool_lock = Lock()

@utils.private
def action(runner):
    if not runner:
        raise RuntimeError("Runner is undefined")
    uid = runner.uid
    interval = runner.interval
    # Beginning of the processing of runner, used to correct next interval, and check against
    # cron expression, it is a beginning of the periodic operation
    begin = utils.currentTimeMillis()
    # Session per thread, have to close it at the end of the procedure
    session = SignallingSession(db)
    try:
        runner.logger.info("Start inspecting runner '%s' with interval %s", uid, interval)
        timetable = Timetable.get(session, uid)
        # Check if timetable is active, if not we skip update, otherwise match date with cron
        if timetable and timetable.status == Timetable.ACTIVE:
            runner.logger.info("Runner '%s' - timetable is active", uid)
            matched = timetable.cronExpression().ismatch(begin)
            if matched:
                # create new job as a copy of job used to create timetable, and also add to
                # timetable statistics, note that we ignore delay, and update name of the job
                runner.logger.debug("Runner '%s' preparing to launch new job", uid)
                copy = Timetable.registerNewJob(session, timetable)
                runner.logger.info("Runner '%s' launched new job '%s' (%s)", uid, copy.name,
                    copy.uid)
            else:
                runner.logger.debug("Runner '%s' skipped update, cron match is False", uid)
        elif timetable and timetable.status == Timetable.PAUSED:
            runner.logger.info("Runner '%s' - timetable is paused", uid)
        # commit all changes made
        session.commit()
    except Exception as e:
        runner.logger.error("Runner '%s' failed to launch", uid)
        runner.logger.exception(e.message)
    finally:
        # Close session after thread is complete
        session.close()
        # Create timer for a subsequent lookup, if runner is still active
        if runner.enabled:
            # compute left seconds for next launch
            secondsElapsed = (begin / 1000) % MINIMAL_INTERVAL
            correctedInterval = MINIMAL_INTERVAL - secondsElapsed
            # Spawning another thread with updated interval
            timer = Timer(correctedInterval, action, [runner])
            timer.daemon = True
            timer.start()
            runner.logger.debug("Runner '%s' spawned another thread", uid)
            runner.logger.debug("Runner '%s' uses updated interval '%.3f' <= (%.3f)",
                uid, correctedInterval, secondsElapsed)
        else:
            runner.logger.debug("Runner '%s' has been disabled", uid)
            runner.logger.debug("Runner '%s' requested clean up", uid)
            runner = None

# Unit of execution, assigned to a particular timetable
class TimetableRunner(Loggable, object):
    def __init__(self, uid, interval):
        super(TimetableRunner, self).__init__()
        self.uid = uid
        self.interval = interval
        self.enabled = False
        # Start after initialization
        self.start()

    def start(self):
        if self.enabled:
            self.logger.warn("Runner '%s' already running", self.uid)
            return None
        self.enabled = True
        action(self)

    def stop(self):
        self.enabled = False

# Timetable scheduler, once started, fetches all non-cancelled timetables and launches processes for
# every one of them with 60 seconds interval. If timetable is paused thread is not killed and keeps
# running, though it stops lauching jobs. Once timetable is cancelled it is updated and removed from
# the pool. Once new timetable is created, it is registered in the scheduler pool.
scheduler = Loggable("timetable-scheduler")
scheduler.pool = {}

# Add new timetable and register new runner for the pool
@utils.private
def addToPool(uid):
    try:
        pool_lock.acquire()
        if uid and uid not in scheduler.pool:
            scheduler.pool[uid] = TimetableRunner(uid, MINIMAL_INTERVAL)
            scheduler.logger.info("Launched runner '%s'", uid)
        elif uid and uid in scheduler.pool:
            scheduler.logger.warn("Attempt to launch already added runner '%s', skipped", uid)
        else:
            scheduler.logger.error("Invalid uid '%s', runner could not be launched" % uid)
    finally:
        pool_lock.release()

# Remove cancelled runner from the pool to clean it up
@utils.private
def removeFromPool(uid):
    try:
        pool_lock.acquire()
        if uid not in scheduler.pool:
            scheduler.logger.warn("Requested to remove non-existent runner '%s'", uid)
        else:
            scheduler.pool[uid].stop()
            del scheduler.pool[uid]
            scheduler.logger.info("Removed runner '%s' from the pool", uid)
    finally:
        pool_lock.release()

# Generic start function, pulls all active/paused timetables and registers runners
def start():
    # We pull all non-cancelled jobs from it to spawn new scheduling threads
    session = SignallingSession(db)
    timetables = Timetable.listEnabled(session)
    session.close()
    for timetable in timetables:
        addToPool(timetable.uid)
    scheduler.logger.info("Timetable scheduler is started")

# Generic stop function, performs clean up of the pool
def stop():
    for uid in scheduler.pool.keys():
        removeFromPool(key)
    # Reset pool
    scheduler.pool = {}
    scheduler.logger.info("Timetable scheduler is stopped")
