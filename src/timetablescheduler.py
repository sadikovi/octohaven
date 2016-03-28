#!/usr/bin/env python

import utils
from loggable import Loggable
from threading import Timer, Lock
from timetable import Timetable
from octohaven import ee, db

# Minimal interval for timetable scheduling, it does not make sense keep it less than 1 minute
MINIMAL_INTERVAL = 5.0

# Action lock for all runners
lock = Lock()
# Pool lock for updates
pool_lock = Lock()

def action(runner):
    if not runner:
        raise RuntimeError("Runner is undefined")
    uid = runner.uid
    interval = runner.interval

    try:
        lock.acquire()
        runner.logger.info("Inspecting runner '%s' with interval %s", uid, interval)
        # timetable = Timetable.get(uid)
        timetable = None
        if timetable:
            if timetable.status == Timetable.ACTIVE:
                runner.logger.info("Runner: '%s' - timetable is active", uid)
                runner.logger.info("json: %s", timetable.json())
            elif timetable.status == Timetable.PAUSED:
                runner.logger.info("Runner: '%s' - timetable is paused", uid)
                runner.logger.info("json: %s", timetable.json())
    except Exception as e:
        runner.logger.error("Runner '%s' failed to launch", uid)
        runner.logger.exception(e.message)
    finally:
        lock.release()
        # Create timer for a subsequent lookup, if runner is still active
        if runner.enabled:
            timer = Timer(MINIMAL_INTERVAL, action, [runner])
            timer.daemon = True
            timer.start()
            runner.logger.debug("Runner '%s' spawned another thread", runner.uid)
        else:
            runner.logger.debug("Runner '%s' has been disabled", runner.uid)
            runner.logger.debug("Runner '%s' requested clean up", runner.uid)
            runner = None

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
class TimetableScheduler(Loggable, object):
    def __init__(self):
        super(TimetableScheduler, self).__init__()
        # Pool is a dictionary with key being timetable id and value being a thread
        self.pool = {}

    # Generic sequence launcher
    def launch(self, timetables):
        for timetable in timetables:
            self.addToPool(timetable.uid)

    # Add new timetable and register new runner for the pool
    def addToPool(self, uid):
        try:
            pool_lock.acquire()
            if uid:
                self.logger.info("Launching runner for timetable '%s'", uid)
                self.pool[uid] = TimetableRunner(uid, MINIMAL_INTERVAL)
            else:
                self.logger.error("Invalid uid %s, runner could not be launched" % uid)
        finally:
            pool_lock.release()

    # Remove cancelled runner from the pool to clean it up
    # use pool lock just to be safe
    def removeFromPool(self, uid):
        try:
            pool_lock.acquire()
            if uid not in self.pool:
                self.logger.warn("Requested to remove non-existent runner '%s'", uid)
            else:
                self.pool[uid].stop()
                del self.pool[uid]
                self.logger.info("Removed runner '%s' from the pool", uid)
        finally:
            pool_lock.release()

    # Generic start function, pulls all active / paused timetables and registers runners
    def start(self):
        # We pull all non-cancelled jobs from it to spawn new scheduling threads
        self.launch(Timetable.listEnabled())

    # Generic stop function, performs clean up of the pool
    def stop(self):
        for key, runner in self.pool.items():
            runner.stop()
            self.logger.debug("Stopped and removed runner '%s' from the pool", key)
            runner = None
        # Reset pool
        self.pool = {}
