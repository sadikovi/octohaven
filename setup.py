#!/usr/bin/env python

import sys, unittest, paths
from cli import CLI
from src.octo.mysqlcontext import MySQLContext

# tables for the application
TABLE_TEMPLATES = ("templates", (
    "create table if not exists templates ("
    "   uid int unsigned auto_increment primary key,"
    "   name varchar(255),"
    "   createtime bigint unsigned,"
    "   content varchar(4000)"
    ") engine = InnoDB, comment = 'Templates';"
))

TABLE_SPARKJOBS = ("sparkjobs", (
    "create table if not exists sparkjobs ("
    "    uid int unsigned auto_increment primary key,"
    "    name varchar(255),"
    "    entrypoint varchar(1024),"
    "    jar varchar(1024),"
    "    options varchar(2000),"
    "    jobconf varchar(2000)"
    ") engine = InnoDB, comment = 'Spark jobs';"
))

TABLES_JOBS = ("jobs", (
    "create table if not exists jobs ("
    "    uid int unsigned auto_increment primary key,"
    "    name varchar(255),"
    "    status varchar(30),"
    "    createtime bigint unsigned,"
    "    submittime bigint unsigned,"
    "    starttime bigint unsigned,"
    "    finishtime bigint unsigned,"
    "    sparkjob int unsigned,"
    "    priority bigint,"
    "    sparkappid varchar(255),"
    "    foreign key fk_jobs_sparkjob (sparkjob)"
    "        references sparkjobs(uid)"
    ") engine = InnoDB, comment = 'Jobs';"
))

TABLES_TIMETABLES = ("timetables", (
    "create table if not exists timetables ("
    "    uid int unsigned auto_increment primary key,"
    "    name varchar(255),"
    "    status varchar(30),"
    "    clonejob int unsigned,"
    "    starttime bigint unsigned,"
    "    stoptime bigint unsigned,"
    "    cron_pattern varchar(255),"
    "    cron_minute tinyint unsigned,"
    "    cron_hour tinyint unsigned,"
    "    cron_day tinyint unsigned,"
    "    cron_month tinyint unsigned,"
    "    cron_weekday tinyint unsigned,"
    "    cron_year smallint,"
    "    foreign key fk_timetables_clonejob (clonejob)"
    "        references jobs(uid)"
    ") engine = InnoDB, comment = 'Timetables';"
))

TABLES_TIMETABLE_JOB = ("timetable_job", (
    "create table if not exists timetable_job ("
    "    abs_order int unsigned auto_increment unique key,"
    "    timetable int unsigned,"
    "    job int unsigned,"
    "    createtime bigint unsigned,"
    "    primary key (timetable, job),"
    "    foreign key fk_timetable_job_timetable (timetable)"
    "        references timetables(uid),"
    "    foreign key fk_timetable_job_job (job)"
    "        references jobs(uid)"
    ") engine = InnoDB, comment = 'Bridge table for timetable-job pairs';"
))

TABLES = [TABLE_TEMPLATES, TABLE_SPARKJOBS, TABLES_JOBS, TABLES_TIMETABLES, TABLES_TIMETABLE_JOB]

# Load tables using MySQLContext.
# if "drop_existing" is True, every time function runs, it will delete existing tables, otherwise
# it will ignore table creation.
# if "logging" is True, it will print out status messages
def loadTables(sqlContext, drop_existing=False, logging=False):
    if drop_existing:
        if logging:
            print "[WARN] Remove previous tables"
        # drop tables
        for name, ddl in reversed(TABLES):
            sqlContext.dropTable(name)

    # create tables
    for name, ddl in TABLES:
        if logging:
            print "[INFO] Creating table '%s'" % name
        status = sqlContext.createTable(ddl)
        # report status, if available
        if logging:
            if status:
                print "- Created '%s'" % name
            else:
                print "- Table '%s' already exists" % name

if __name__ == '__main__':
    cli = CLI(sys.argv[1:])
    config = {
        "host": cli.get("host"),
        "port": cli.get("port"),
        "user": cli.get("user"),
        "password": cli.get("password"),
        "database": cli.get("database")
    }
    # other options
    drop_existing = cli.get("drop_existing")

    print "[INFO] Setup MySQL instance..."
    print "[INFO] Using configuration:"
    print " host: %s" % config["host"]
    print " port: %s" % config["port"]
    print " user: %s" % config["user"]
    print " password: %s" % "*****"
    print " database: %s" % config["database"]

    sqlcnx = MySQLContext(**config)
    loadTables(sqlcnx, drop_existing, logging=True)
    print "[INFO] Done"
