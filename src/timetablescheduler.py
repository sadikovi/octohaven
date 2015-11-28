#!/usr/bin/env python

from octolog import Octolog
from threading import Timer, Lock
from paths import LOGS_PATH
from redisconnector import RedisConnector, RedisConnectionPool
from storagemanager import StorageManager
from sparkmodule import SparkModule
from jobmanager import JobManager
from timetable import *
from subscription import Subscriber, GLOBAL_DISPATCHER
from utils import *

MINIMAL_INTERVAL = 60.0

# general lock for all runners
lock = Lock()
# default running action
def action(runner):
    uid, currenttime, interval = None, None, MINIMAL_INTERVAL
    try:
        lock.acquire()
        # update uid, and current time for reference
        uid = runner.uid
        interval = runner.interval
        currenttime = currentTimeMillis()
        # check timetable
        timetable = runner.manager.timetableForUid(uid)
        if not timetable:
            raise StandardError("No timetable found for uid: %s" % uid)
        # assess status
        status = timetable.status
        active = status == TIMETABLE_ACTIVE
        runner.stopped = status == TIMETABLE_CANCELED
        # show statistics for runner
        runner.logger().debug("[%s at %s] statistics - active: %s, stopped: %s", uid, currenttime,
            active, runner.stopped)
        if not runner.stopped:
            if active:
                runner.logger().debug("[%s at %s] status is active, run action", uid, currenttime)
                # compare pattern with current time
                if timetable.crontab.ismatch(currenttime):
                    # if comparison matches, clone job and schedule it
                    runner.logger().info("[%s at %s] Time matches pattern, clone and launch job",
                        uid, currenttime)
                    # define next job order
                    nextNum = timetable.numJobs if timetable.numJobs is not None else 0
                    jobname = "%s-job-%s" % (timetable.name, nextNum)
                    # clone job
                    clonejob = runner.manager.jobManager.jobForUid(timetable.clonejobid)
                    if not clonejob:
                        raise StandardError("Failed to load clone job %s" % (timetable.clonejobid))
                    newjob = runner.manager.cloneJob(clonejob, jobname)
                    runner.logger().info("[%s at %s] created job %s", uid, currenttime, newjob.uid)
                    # update timetable first
                    timetable.updateRunTime(currenttime)
                    timetable.addJob(newjob)
                    runner.manager.saveTimetable(timetable)
                    # save and schedule job
                    runner.manager.jobManager.saveJob(newjob)
            else:
                runner.logger().debug("[%s at %s] status is inactive, skip", uid, currenttime)
    except Exception as e:
        runner.logger().error("[%s] failed to proceed", uid)
        runner.logger().exception(e.message)
    finally:
        lock.release()
        # Create timer for a subsequent lookup, if runner is still active
        if not runner.stopped:
            # normalize interval
            inteval = interval if interval >= MINIMAL_INTERVAL else MINIMAL_INTERVAL
            timer = Timer(interval, action, [runner])
            timer.daemon = True
            timer.start()
            runner.logger().debug("[%s] spawned another thread", uid)
        else:
            runner.logger().debug("[%s] has been shut down", uid)
            runner = None

class TimetableRunner(Octolog, object):
    def __init__(self, uid, interval, manager, stopped):
        self.uid = uid
        self.interval = interval
        # timetable manager to schedule timetable and create jobs
        self.manager = manager
        self.stopped = stopped
        # spawn process
        action(self)

# Timetable scheduler, once started, fetches all non-canceled timetables and launches processes for
# every one of them with 60 seconds interval. If timetable is paused thread is not killed and keeps
# running, though it stops lauching jobs. Once timetable is canceled it is updated and removed from
# the pool. Once new timetable is created, it is registered in the scheduler pool.
class TimetableScheduler(Subscriber, object):
    def __init__(self, settings):
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
        storageManager = StorageManager(connector)
        sparkModule = SparkModule(sparkMaster, sparkUi, sparkUiRun)
        self.jobManager = JobManager(sparkModule, storageManager)
        self.timetableManager = TimetableManager(self.jobManager)
        # pool is a dictionary with key being timetable id and value being a thread
        self.pool = {}
        # register with dispatcher
        Subscriber.__init__(self, GLOBAL_DISPATCHER)
        # register to "create timetable" event
        self.subscribe("timetable-create", future=True)

    def start(self):
        # when we start scheduler we pull all non-canceled jobs from it to spawn new scheduling
        # threads
        arr = self.timetableManager.listTimetables([TIMETABLE_ACTIVE, TIMETABLE_PAUSED])
        # each thread needs timetable id, interval, manager
        for timetable in arr:
            self.addTimetableToPool(timetable)

    def addTimetableToPool(self, timetable):
        if type(timetable) is not Timetable:
            self.logger().error("Expected Timetable, got %s", str(type(timetable)))
            return None
        uid = timetable.uid
        stopped = timetable.status == TIMETABLE_CANCELED
        # refresh interval in seconds (constant for now)
        interval = 60.0
        self.logger().debug("Launching runner %s", uid)
        self.pool[uid] = TimetableRunner(uid, interval, self.timetableManager, stopped)

    # subscriber action method
    def receive(self, event, value):
        if event == "timetable-create":
            self.addTimetableToPool(value)

    def stop(self):
        for key, runner in self.pool.items():
            if runner:
                runner.active = False
                runner.stopped = True
                self.logger().debug("Stopped %s runner", runner.uid)
        # reset pool
        self.pool = {}
