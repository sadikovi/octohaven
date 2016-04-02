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

import sys, os, utils, urllib2
from flask import Flask, redirect, render_template, make_response, json, jsonify, abort, request, send_from_directory
from sqlalchemy import desc
from config import VERSION, API_VERSION
from loggable import Loggable
from sparkmodule import SparkContext
from sqlmodule import MySQLContext
from fs import FileManager, BlockReader
from encoders import CustomJSONEncoder
from pyee import EventEmitter
from shutdown import GracefulShutdown

################################################################
# Application setup
################################################################
app = Flask("octohaven")
app.config.from_object("config.Options")
app.json_encoder = CustomJSONEncoder
# prepare logger for application
app_log = Loggable("octohaven")

# log global parameters
app_log.logger.info("Host - %s" % app.config["HOST"])
app_log.logger.info("Port - %s" % app.config["PORT"])
app_log.logger.info("Spark Master - %s" % app.config["SPARK_MASTER_ADDRESS"])
app_log.logger.info("Spark UI - %s" % app.config["SPARK_UI_ADDRESS"])
app_log.logger.info("Spark Submit - %s" % app.config["SPARK_SUBMIT"])
app_log.logger.info("Jar folder - %s" % app.config["JAR_FOLDER"])
app_log.logger.info("Working directory - %s" % app.config["WORKING_DIR"])
app_log.logger.info("MySQL connection - host - %s" % app.config["MYSQL_HOST"])
app_log.logger.info("MySQL connection - port - %s" % app.config["MYSQL_PORT"])
app_log.logger.info("MySQL connection - database - %s" % app.config["MYSQL_DATABASE"])
app_log.logger.info("MySQL connection - user - %s" % app.config["MYSQL_USER"])
app_log.logger.info("MySQL connection - password - %s" % "*******")

# Spark module is one per application, currently UI Run address is not supported, so we pass UI
# address as dummy value
sparkContext = SparkContext(app.config["SPARK_MASTER_ADDRESS"], app.config["SPARK_UI_ADDRESS"],
    app.config["SPARK_UI_ADDRESS"], app.config["SPARK_SUBMIT"])
# SQL context is one per application
db = MySQLContext(application=app, host=app.config["MYSQL_HOST"],
    port=app.config["MYSQL_PORT"], database=app.config["MYSQL_DATABASE"],
    user=app.config["MYSQL_USER"], password=app.config["MYSQL_PASSWORD"],
    pool_size=5)
# Global event emitter
ee = EventEmitter()
# Working directory for application
workingDirectory = app.config["WORKING_DIR"]

# Method to return API endpoint (prefix)
def api(suffix):
    return "/api/%s/%s" % (API_VERSION, suffix.strip("/"))

################################################################
# Model
################################################################
from template import Template
from job import Job
from timetable import Timetable

################################################################
# Database and service start
################################################################
if app.config["MYSQL_SCHEMA_RESET"]:
    db.drop_all()
db.create_all()

# Scheduler initialization
from scheduler import tscheduler
from scheduler import jobscheduler

def start():
    @ee.on("timetable-created")
    def addRunner(uid):
        tscheduler.addToPool(uid)

    @ee.on("timetable-cancelled")
    def removeRunner(uid):
        tscheduler.removeFromPool(uid)

    tscheduler.start()
    jobscheduler.start()
    app.run(debug=app.debug, host=app.config["HOST"], port=app.config["PORT"])

def stop():
    app_log.logger.info("Requested application shutdown...")
    try:
        app_log.logger.info("Stop services...")
        tscheduler.stop()
        jobscheduler.stop()
    except:
        print "Application exited with error."
        sys.exit(1)
    else:
        print "Application exited successfully."
        sys.exit(0)

def test():
    import test
    test.main()

################################################################
# Shutdown
################################################################
shutdownHook = GracefulShutdown()
shutdownHook.registerCallback(stop)

################################################################
# Pages routing
################################################################
# Render page with parameters passed, base template parameters automatically added
def render_page(page, **params):
    return render_template(page,
        version=VERSION,
        spark_ui=app.config["SPARK_UI_ADDRESS"],
        spark_master=app.config["SPARK_MASTER_ADDRESS"],
        cluster_status=sparkContext.clusterStatus(),
        **params)

# Additional static folder with external dependencies
@app.route("/static/external/<path:filepath>")
def static_external(filepath):
    return send_from_directory("bower_components", filepath)

@app.route("/")
def index():
    return redirect("/jobs")

@app.route("/jobs")
def jobs_for_status():
    return render_page("jobs.html")

@app.route("/timetables")
def timetables_for_status():
    return render_page("timetables.html")

@app.route("/create/job")
def create_job():
    return render_page("create_job.html")

# Redirect to default create page, which will give instructions on how to create timetables
@app.route("/create/timetable")
def create_timetable():
    return render_page("create_timetable.html", job="")

@app.route("/create/timetable/job/<int:uid>")
def create_timetable_job(uid):
    job = Job.get(db.session, uid)
    dump = json.dumps(job.json()) if job else ""
    return render_page("create_timetable.html", job=dump)

@app.route("/job/<int:uid>")
def job_for_uid(uid):
    job = Job.get(db.session, uid)
    dump = json.dumps(job.json()) if job else ""
    return render_page("job.html", job=dump)

@app.route("/timetable/<int:uid>")
def timetable_for_uid(uid):
    timetable = Timetable.get(db.session, uid)
    dump = json.dumps(timetable.json()) if timetable else ""
    return render_page("timetable.html", timetable=dump)

# Job actions (viewing stdout and stderr)
@app.route("/job/<int:uid>/stdout")
@app.route("/job/<int:uid>/stderr")
def job_stdlogs(uid):
    job = Job.get(db.session, uid)
    dump = json.dumps(job.json()) if job else ""
    jobName = job.name if job else ""
    title = request.path.upper().split("/")[-1]
    return render_page("job_console.html", title=title, uid=uid, name=jobName, job=dump)

################################################################
# REST API
################################################################
# successful response helper
def success(payload):
    return make_response(jsonify(payload), 200)

@app.errorhandler(StandardError)
def standard_error(error):
    app_log.logger.exception("StandardError: %s", error.message)
    return make_response(jsonify({"code": 400, "msg": "%s" % error.message}), 400)

@app.errorhandler(BaseException)
def base_exception(error):
    app_log.logger.exception("Exception occuried: %s", error.message)
    return make_response(jsonify({"code": 500, "msg": "%s" % error.message}), 500)

################################################################
# Spark API
################################################################
@app.route(api("/spark/status"), methods=["GET"])
def spark_status():
    status = sparkContext.clusterStatus()
    return success({"status": status})

################################################################
# Finder API
################################################################
@app.route(api("/finder/home"), methods=["GET"])
@app.route(api("/finder/home/<path:rel_path>"), methods=["GET"])
def finder_home_path(rel_path=None):
    # in case of root request "home" we return empty list
    parts = rel_path.split("/") if rel_path else []
    manager = FileManager(app.config["JAR_FOLDER"], alias="/api/v1/finder/home",
        extensions=[".jar"], showOneNode=False)
    tree, lstree = manager.ls(*parts)
    return success({"path": tree, "ls": lstree})

################################################################
# Job API
################################################################
@app.route(api("/job/list"), methods=["GET"])
def job_list():
    status = request.args.get("status")
    resolvedStatus = status.upper() if status and status.upper() != "ALL" else None
    return success({"data": [x.json() for x in Job.list(db.session, status)]})

@app.route(api("/job/create"), methods=["POST"])
def job_create():
    obj = request.get_json()
    job = Job.create(db.session, **obj)
    return success(job.json())

@app.route(api("/job/get/<int:uid>"), methods=["GET"])
def job_get(uid):
    job = Job.get(db.session, uid)
    if not job: raise StandardError("No job for id '%s'" % uid)
    return success(job.json())

@app.route(api("/job/close/<int:uid>"), methods=["GET"])
def job_close(uid):
    job = Job.get(db.session, uid)
    if not job:
        raise StandardError("No job for id '%s'" % uid)
    Job.close(db.session, job)
    return success(job.json())

# API to serve log files (stdout and stderr) for a job
@app.route(api("/job/log/<int:uid>/<logtype>/page/<int:page>"), methods=["GET"])
def job_log(uid, logtype, page):
    logtype = logtype.upper()
    if not logtype or (logtype != "STDOUT" and logtype != "STDERR"):
        raise StandardError("Invalid log type, expected either 'stdout' or 'stderr'")
    if not page:
        raise StandardError("Unrecognized page number '%s'" % page)
    # Fetch job for uid
    job = Job.get(db.session, uid)
    if not job:
        raise StandardError("No job for id '%s'" % uid)
    # Looking up file and creating output
    suffix = jobscheduler.STDOUT if logtype == "STDOUT" else jobscheduler.STDERR
    path = os.path.join(jobscheduler.jobWorkingDirectory(uid), suffix)
    if not os.path.isfile(path):
        raise StandardError("No logs found for job id '%s'" % uid)
    block, numPages = "", -1
    chunk, offset = 64*1024, 128
    manager = BlockReader()
    with open(path, "rb") as f:
        numPages = manager.numPages(f, chunk)
        block = manager.readFromStart(f, page, chunk, offset)
    # Current page API url
    current_page_url = api("/job/log/%s/%s/page/%s" % (job.uid, logtype, page))
    # Next page API url
    next_page_url = api("/job/log/%s/%s/page/%s" % (job.uid, logtype, page + 1)) \
        if page < numPages else None
    # Previous page API url
    prev_page_url = api("/job/log/%s/%s/page/%s" % (job.uid, logtype, page - 1)) \
        if page > 1 else None
    # Jump-to-page url
    jump_to_page_url = api("/job/log/%s/%s/page/_page_" % (job.uid, logtype))
    return success({"uid": job.uid, "name": job.name, "type": logtype, "pages": numPages,
        "page": page, "block": block, "size": chunk, "next_page_url": next_page_url,
        "prev_page_url": prev_page_url, "current_page_url": current_page_url,
        "jump_to_page_url": jump_to_page_url})

################################################################
# Template API
################################################################
@app.route(api("/template/list"), methods=["GET"])
def template_list():
    templates = Template.list()
    return success({"data": [x.json() for x in templates]})

@app.route(api("/template/create"), methods=["POST"])
def template_create():
    opts = request.get_json()
    name = opts["name"] if "name" in opts else None
    template = Template.create(name=name, content=json.dumps(opts))
    return success(template.json())

@app.route(api("/template/delete/<int:uid>"), methods=["GET"])
def template_delete(uid):
    template = Template.get(uid)
    if not template:
        raise StandardError("No template for id '%s'" % uid)
    Template.delete(template)
    return success(template.json())

@app.route(api("/template/delete_and_list/<int:uid>"), methods=["GET"])
def template_delete_and_list(uid):
    template = Template.get(uid)
    if not template:
        raise StandardError("No template for id '%s'" % uid)
    Template.delete(template)
    return template_list()

################################################################
# Timetable API
################################################################
@app.route(api("/timetable/create"), methods=["POST"])
def timetable_create():
    opts = request.get_json()
    timetable = Timetable.create(db.session, **opts)
    return success(timetable.json())

@app.route(api("/timetable/list"), methods=["GET"])
def timetable_list():
    status = request.args.get("status")
    resolvedStatus = status.upper() if status and status.upper() != "ALL" else None
    timetables = Timetable.list(db.session, resolvedStatus)
    return success({"data": [x.json() for x in timetables]})

@app.route(api("/timetable/get/<int:uid>"), methods=["GET"])
def timetable_get(uid):
    timetable = Timetable.get(db.session, uid)
    if not timetable:
        raise StandardError("No timetable for id '%s'" % uid)
    return success(timetable.json())

@app.route(api("/timetable/<action>/<int:uid>"), methods=["GET"])
def timetable_action(action, uid):
    timetable = Timetable.get(db.session, uid)
    if not timetable:
        raise StandardError("No timetable for id '%s'" % uid)
    if action == "pause":
        Timetable.pause(db.session, timetable)
    elif action == "resume":
        Timetable.resume(db.session, timetable)
    elif action == "cancel":
        Timetable.cancel(db.session, timetable)
    else:
        raise StandardError("Invalid action '%s'" % action)
    return success(timetable.json())
