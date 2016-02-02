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

from extlogging import Loggable

# Logging for SQL schema
schema_log = Loggable("SQL Schema")

################################################################
# Application SQL Schema
################################################################
TABLE_TEMPLATES = ("templates", (
    "create table if not exists templates ("
    "   uid int unsigned auto_increment primary key,"
    "   name varchar(255),"
    "   createtime bigint,"
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
    "    createtime bigint,"
    "    submittime bigint,"
    "    starttime bigint,"
    "    finishtime bigint,"
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
    "    starttime bigint,"
    "    stoptime bigint,"
    "    cron_pattern varchar(255),"
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

# Load tables using SQLContext.
# if "drop_existing" is True, every time function runs, it will delete existing tables, otherwise
# it will ignore table creation.
# option "suppress_log" will suppress output even if logging level is debug.
def loadSchema(sqlContext, drop_existing=False, suppress_log=False):
    if drop_existing:
        schema_log.logger.info("Drop existing tables")
        for name, ddl in reversed(TABLES):
            if not suppress_log:
                schema_log.logger.debug("- Dropping table '%s'", name)
            sqlContext.dropTable(name)
            if not suppress_log:
                schema_log.logger.debug("- Table '%s' dropped", name)
    schema_log.logger.info("Check/create schema")
    for name, ddl in TABLES:
        status = sqlContext.createTable(ddl)
        if status:
            if not suppress_log:
                schema_log.logger.debug("- Created table '%s'", name)
        else:
            if not suppress_log:
                schema_log.logger.debug("- Table '%s' already exists", name)
