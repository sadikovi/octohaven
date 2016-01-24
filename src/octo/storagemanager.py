#!/usr/bin/env python

import src.octo.utils as utils
from types import DictType
from src.octo.mysqlcontext import MySQLContext

MAX_FETCH_RECORDS = 1000

# Storage manager is data provider to MySQLContext. It manages all the queries in the
# application.
class StorageManager(object):
    def __init__(self, sqlContext):
        utils.assertInstance(sqlContext, MySQLContext)
        self.sqlContext = sqlContext

    ############################################################
    # Template API
    ############################################################
    # Insert data [name: String, createtime: Long, content: String] into table and return
    # new id for that template
    def createTemplate(self, name, createtime, content):
        rowid = None
        with self.sqlContext.cursor(with_transaction=True) as cr:
            dml = ("INSERT INTO templates(name, createtime, content) "
                    "VALUES(%(name)s, %(createtime)s, %(content)s)")
            cr.execute(dml, {"name": name, "createtime": createtime, "content": content})
            rowid = cr.lastrowid
        return rowid

    # Fetch all available templates [uid, name, createtime, content] and sort them by name.
    # Return results as list of dict objects with fields similar to schema.
    def getTemplates(self):
        data = None
        with self.sqlContext.cursor(with_transaction=False) as cr:
            sql = "SELECT uid, name, createtime, content FROM templates ORDER BY name ASC"
            cr.execute(sql)
            data = cr.fetchall()
        return data

    # Fetch one record [uid, name, createtime, content] based on uid provided. Return dict object
    # with fields given as column names.
    def getTemplate(self, uid):
        data = None
        with self.sqlContext.cursor(with_transaction=False) as cr:
            sql = "SELECT uid, name, createtime, content FROM templates WHERE uid = %(uid)s"
            cr.execute(sql, {"uid": uid})
            data = cr.fetchone()
        return data

    # Delete record based on uid specified
    def deleteTemplate(self, uid):
        with self.sqlContext.cursor(with_transaction=True) as cr:
            dml = "DELETE FROM templates WHERE uid = %(uid)s"
            cr.execute(dml, {"uid": uid})

    ############################################################
    # Job API
    ############################################################
    # Insert data of SparkJob and Job dictionaries into "sparkjob" and "job" tables
    def createJob(self, dummySparkJobDict, dummyJobDict):
        utils.assertInstance(dummySparkJobDict, DictType)
        utils.assertInstance(dummyJobDict, DictType)
        rowid = None
        with self.sqlContext.cursor(with_transaction=True) as cr:
            # 1. store Spark job and retrieve id
            dml1 = ("INSERT INTO sparkjobs(name, entrypoint, jar, options, jobconf) "
                "VALUES(%(name)s, %(entrypoint)s, %(jar)s, %(options)s, %(jobconf)s)")
            cr.execute(dml1, dummySparkJobDict)
            # 2. update SparkJob id in Job dictionary
            dummyJobDict["sparkjob"] = cr.lastrowid
            # 3. store Job data and return new uid
            dml2 = ("INSERT INTO jobs(name, status, createtime, submittime, starttime, "
                "finishtime, sparkjob, priority, sparkappid) "
                "VALUES(%(name)s, %(status)s, %(createtime)s, %(submittime)s, %(starttime)s, "
                "%(finishtime)s, %(sparkjob)s, %(priority)s, %(sparkappid)s)")
            cr.execute(dml2, dummyJobDict)
            rowid = cr.lastrowid
        return rowid

    # Update status for job uid
    def updateStatus(self, uid, status):
        with self.sqlContext.cursor(with_transaction=True) as cr:
            # 1. check that job uid exists
            sql = "SELECT uid FROM jobs WHERE uid = %(uid)s"
            cr.execute(sql, {"uid": uid})
            data = cr.fetchone()
            if not data:
                raise StandardError("Job uid '%s' does not exist" % uid)
            # 2. update status for that job
            dml = "UPDATE jobs SET status = %(status)s WHERE uid = %(uid)s"
            cr.execute(dml, {"uid": uid, "status": status})

    # Update status and finish time for job uid. Expected status FINISHED
    def updateStatusAndFinishTime(self, uid, status, ftime):
        with self.sqlContext.cursor(with_transaction=True) as cr:
            # 1. check that job uid exists
            sql = "SELECT uid FROM jobs WHERE uid = %(uid)s"
            cr.execute(sql, {"uid": uid})
            data = cr.fetchone()
            if not data:
                raise StandardError("Job uid '%s' does not exist" % uid)
            # 2. update status for that job
            dml = "UPDATE jobs SET status = %(status)s, finishtime = %(ftime)s WHERE uid = %(uid)s"
            cr.execute(dml, {"uid": uid, "status": status, "ftime": ftime})

    # Fetch job for a specific uid. Including Spark job can be specified using "withSparkJob"
    def getJob(self, uid, withSparkJob=True):
        data = None
        with self.sqlContext.cursor(with_transaction=False) as cr:
            if withSparkJob:
                sql = """
                    SELECT
                        j.uid, j.name, j.status, j.createtime, j.submittime, j.starttime,
                        j.finishtime, j.sparkjob, j.priority, j.sparkappid,
                        s.uid as spark_uid, s.name as spark_name, s.entrypoint as spark_entrypoint,
                        s.jar as spark_jar, s.options as spark_options, s.jobconf as spark_jobconf
                    FROM jobs j INNER JOIN sparkjobs s ON s.uid = j.sparkjob
                    WHERE j.uid = %(uid)s"""
            else:
                sql = ("SELECT uid, name, status, createtime, submittime, starttime, finishtime, "
                    "sparkjob, priority, sparkappid FROM jobs WHERE uid = %(uid)s")
            cr.execute(sql, {"uid": uid})
            data = cr.fetchone()
        return data

    # Get all jobs sorted by create time
    def getJobsByCreateTime(self, limit, desc=True):
        return self.getJobsByStatusCreateTime(None, limit, desc)

    # Get jobs by status sorted by create time
    def getJobsByStatusCreateTime(self, status, limit, desc=True):
        data = None
        orderBy = "DESC" if desc else "ASC"
        limitBy = limit if limit > 0 and limit < MAX_FETCH_RECORDS else MAX_FETCH_RECORDS
        with self.sqlContext.cursor(with_transaction=False) as cr:
            if not status:
                sql = """SELECT uid, name, status, createtime, submittime, starttime, finishtime,
                    sparkjob, priority, sparkappid FROM jobs
                    ORDER BY createtime %s LIMIT %s""" % (orderBy, limitBy)
            else:
                sql = """SELECT uid, name, status, createtime, submittime, starttime, finishtime,
                    sparkjob, priority, sparkappid FROM jobs WHERE status = %(status)s """ + \
                    "ORDER BY createtime %s LIMIT %s" % (orderBy, limitBy)
            cr.execute(sql, {"status": status})
            data = cr.fetchall()
        return data

    ############################################################
    # Timetable API
    ############################################################
    def createTimetable(self, dct):
        rowid = None
        with self.sqlContext.cursor(with_transaction=True) as cr:
            dml = ("INSERT INTO timetables(name, status, clonejob, starttime, stoptime, "
                "cron_pattern) VALUES(%(name)s, %(status)s, %(clonejob)s, %(starttime)s, "
                "%(stoptime)s, %(cron_pattern)s)")
            cr.execute(dml, dct)
            rowid = cr.lastrowid
        return rowid

    def getTimetable(self, uid):
        data = None
        with self.sqlContext.cursor(with_transaction=False) as cr:
            sql = ("SELECT uid, name, status, clonejob, starttime, stoptime, cron_pattern "
                    "FROM timetables WHERE uid = %(uid)s")
            cr.execute(sql, {"uid": uid})
            data = cr.fetchone()
        return data

    def getTimetables(self, status):
        data = None
        with self.sqlContext.cursor(with_transaction=False) as cr:
            if not status:
                sql = ("SELECT uid, name, status, clonejob, starttime, stoptime, cron_pattern "
                        "FROM timetables ORDER BY name ASC")
            else:
                sql = ("SELECT uid, name, status, clonejob, starttime, stoptime, cron_pattern "
                        "FROM timetables WHERE status = %(status)s ORDER BY name ASC")
            cr.execute(sql, {"status": status})
            data = cr.fetchall()
        return data

    def updateTimetable(self, dct):
        with self.sqlContext.cursor(with_transaction=True) as cr:
            dml = ("UPDATE timetables SET status = %(status)s, stoptime = %(stoptime)s "
                    "WHERE uid = %(uid)s")
            cr.execute(dml, dct)
