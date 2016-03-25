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

from flask import Flask, redirect, render_template, make_response, json, jsonify, abort, request, send_from_directory
from sqlalchemy import desc
from config import VERSION
from extlogging import Loggable
from sparkmodule import SparkContext
from sqlmodule import MySQLContext
from fs import FileManager
from types import ListType, DictType, LongType
import utils, shlex

################################################################
# Application setup
################################################################
app = Flask("octohaven")
app.config.from_object("config.Options")
# prepare logger for application
app_log = Loggable("octohaven")

# log global parameters
app_log.logger.info("Host - %s" % app.config["HOST"])
app_log.logger.info("Port - %s" % app.config["PORT"])
app_log.logger.info("Spark Master - %s" % app.config["SPARK_MASTER_ADDRESS"])
app_log.logger.info("Spark UI - %s" % app.config["SPARK_UI_ADDRESS"])
app_log.logger.info("Jar folder - %s" % app.config["JAR_FOLDER"])
app_log.logger.info("MySQL connection - host - %s" % app.config["MYSQL_HOST"])
app_log.logger.info("MySQL connection - port - %s" % app.config["MYSQL_PORT"])
app_log.logger.info("MySQL connection - database - %s" % app.config["MYSQL_DATABASE"])
app_log.logger.info("MySQL connection - user - %s" % app.config["MYSQL_USER"])
app_log.logger.info("MySQL connection - password - %s" % "*******")

# Spark module is one per application, currently UI Run address is not supported, so we pass UI
# address as dummy value
sparkContext = SparkContext(app.config["SPARK_MASTER_ADDRESS"], app.config["SPARK_UI_ADDRESS"],
    app.config["SPARK_UI_ADDRESS"])
# SQL context is one per application
db = MySQLContext(application=app, host=app.config["MYSQL_HOST"],
    port=app.config["MYSQL_PORT"], database=app.config["MYSQL_DATABASE"],
    user=app.config["MYSQL_USER"], password=app.config["MYSQL_PASSWORD"],
    pool_size=5)

################################################################
# Model
################################################################
class Template(db.Model):
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    createtime = db.Column(db.BigInteger, nullable=False)
    content = db.Column(db.String(4000), nullable=True)

    def __init__(self, name, createtime, content):
        self.name = name
        self.createtime = createtime
        self.content = content

    # Get canonical name for the template
    @staticmethod
    def getCanonicalName(name):
        name = str(name).strip() if name else ""
        return utils.heroku() if len(name) == 0 else name

    @staticmethod
    @utils.sql
    def add(db, **opts):
        template = Template(opts["name"], utils.currentTimeMillis(), opts["content"])
        db.session.add(template)
        db.session.commit()
        return template

    @classmethod
    @utils.sql
    def list(cls):
        return cls.query.order_by(desc(cls.createtime)).all()

    @classmethod
    @utils.sql
    def get(cls, uid):
        return cls.query.get(uid)

    @staticmethod
    @utils.sql
    def delete(db, template):
        db.session.delete(template)
        db.session.commit()

    def json(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "createtime": self.createtime,
            "content": json.loads(self.content),
            "delete_url": "/api/v1/template/delete/%s" % self.uid,
            "delete_and_list_url": "/api/v1/template/delete_and_list/%s" % self.uid
        }

class Job(db.Model):
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    createtime = db.Column(db.BigInteger, nullable=False)
    submittime = db.Column(db.BigInteger, nullable=False)
    starttime = db.Column(db.BigInteger)
    finishtime = db.Column(db.BigInteger)
    priority = db.Column(db.BigInteger, nullable=False)
    # Spark job options
    sparkappid = db.Column(db.String(255))
    entrypoint = db.Column(db.String(1024), nullable=False)
    jar = db.Column(db.String(1024), nullable=False)
    options = db.Column(db.String(2000), nullable=False)
    jobconf = db.Column(db.String(2000), nullable=False)
    # List of statuses available
    READY = "READY"
    DELAYED = "DELAYED"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    CLOSED = "CLOSED"
    STATUSES = [READY, DELAYED, RUNNING, FINISHED, CLOSED]

    def __init__(self, name, status, priority, createtime, submittime, entrypoint, jar, options,
        jobconf):
        self.name = name
        self.status = status
        self.priority = priority
        self.createtime = createtime
        self.submittime = submittime
        self.entrypoint = entrypoint
        self.jar = jar
        self.options = options
        self.jobconf = jobconf

    def setAppId(self, appId):
        self.sparkappid = appId

    def setStarttime(self, starttime):
        self.starttime = starttime

    def setFinishtime(self, finishtime):
        self.finishtime = finishtime

    # Return Spark options as dictionary
    def getSparkOptions(self):
        return json.loads(self.options)

    # Return Job configuration/options as dictionary
    def getJobConf(self):
        return json.loads(self.jobconf)

    # Get canonical name for the job
    @staticmethod
    def getCanonicalName(name):
        name = str(name).strip() if name else ""
        return "Default Octohaven job" if len(name) == 0 else name

    def canClose(self):
        return self.status == self.READY or self.status == self.DELAYED

    @classmethod
    def new(cls, name, status, priority, createtime, submittime, klass, dmemory, ememory, jar,
        options, jobconf):
        # canonicalize name
        name = cls.getCanonicalName(name)
        # make sure that timestamps are longs
        utils.assertInstance(createtime, LongType)
        utils.assertInstance(submittime, LongType)
        # check status
        if status not in cls.STATUSES:
            raise StandardError("Unrecognized status '%s'" % status)

        # validate priority for the job
        priority = utils.validatePriority(priority)
        # parse Spark options into key-value pairs
        parsedOptions = options if isinstance(options, DictType) else {}
        if not parsedOptions:
            cli = filter(lambda x: len(x) == 2, [x.split("=", 1) for x in shlex.split(str(options))])
            for pre in cli:
                parsedOptions[pre[0]] = pre[1]
        # manually set driver or executor memory takes precedence over Spark options
        parsedOptions["spark.drivery.memory"] = utils.validateMemory(dmemory)
        parsedOptions["spark.executor.memory"] = utils.validateMemory(ememory)
        # parse job configuration/options into list of values
        parsedJobConf = jobconf if isinstance(jobconf, ListType) else shlex.split(str(jobconf))
        # entrypoint for the Spark job
        entrypoint = utils.validateEntrypoint(klass)
        # jar file path
        jar = utils.validateJarPath(jar)

        return cls(name, status, priority, createtime, submittime, entrypoint, jar,
            json.dumps(parsedOptions), json.dumps(parsedJobConf))

    @classmethod
    @utils.sql
    def add(cls, db, **opts):
        job = cls.new(**opts)
        db.session.add(job)
        db.session.commit()
        return job

    @classmethod
    @utils.sql
    def get(cls, uid):
        return cls.query.get(uid)

    @classmethod
    @utils.sql
    def list(cls, status, limit=100):
        filtered = cls.query.filter_by(status = status) if status in cls.STATUSES else cls.query
        limit = limit if limit > 0 else 1
        return filtered.order_by(desc(cls.createtime)).limit(limit).all()

    @classmethod
    @utils.sql
    def close(cls, db, job):
        job.status = cls.CLOSED
        db.session.commit()

    def json(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "status": self.status,
            "createtime": self.createtime,
            "submittime": self.submittime,
            "starttime": self.starttime,
            "finishtime": self.finishtime,
            "priority": self.priority,
            "sparkappid": self.sparkappid,
            "entrypoint": self.entrypoint,
            "jar": self.jar,
            "options": json.loads(self.options),
            "jobconf": json.loads(self.jobconf),
            "url": "/job/%s" % self.uid,
            "close": None if not self.canClose() else "/api/v1/job/close/%s" % self.uid
        }

################################################################
# Database and service start
################################################################
if app.config["MYSQL_SCHEMA_RESET"]:
    db.drop_all()
db.create_all()

def run():
    app.run(debug=app.debug, host=app.config["HOST"], port=app.config["PORT"])

def test():
    import test
    test.main()

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

@app.route("/static/node/<path:filepath>")
def static_node(filepath):
    return send_from_directory("node_modules", filepath)

@app.route("/")
def index():
    return redirect("/jobs")

@app.route("/jobs")
def jobs_for_status():
    return render_page("jobs.html")

@app.route("/create/job")
def create_job():
    return render_page("create_job.html")

@app.route("/job/<int:uid>")
def job_for_uid(uid):
    return render_page("job.html", job=Job.get(uid))

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

# API: Spark status
@app.route("/api/v1/spark/status", methods=["GET"])
def spark_status():
    status = sparkContext.clusterStatus()
    return success({"status": status})

# API: finder (ls tree)
@app.route("/api/v1/finder/home", methods=["GET"])
@app.route("/api/v1/finder/home/<path:rel_path>", methods=["GET"])
def finder_home_path(rel_path=None):
    # in case of root request "home" we return empty list
    parts = rel_path.split("/") if rel_path else []
    manager = FileManager(app.config["JAR_FOLDER"], alias="/api/v1/finder/home",
        extensions=[".jar"], showOneNode=False)
    tree, lstree = manager.ls(*parts)
    return success({"path": tree, "ls": lstree})

# API: fetch jobs
@app.route("/api/v1/job/list", methods=["GET"])
def job_list():
    status = request.args.get("status")
    resolvedStatus = status.upper() if status and status.upper() != "ALL" else None
    return success({"rows": [x.json() for x in Job.list(status)]})

@app.route("/api/v1/job/get/<int:uid>", methods=["GET"])
def job_get(uid):
    job = Job.get(uid)
    if not job:
        raise StandardError("No job for id '%s'" % uid)
    return success(job.json())

@app.route("/api/v1/job/close/<int:uid>", methods=["GET"])
def job_close(uid):
    job = Job.get(uid)
    if not job:
        raise StandardError("No job for id '%s'" % uid)
    Job.close(db, job)
    return success(job.json())

@app.route("/api/v1/job/create", methods=["POST"])
def job_submit():
    obj = request.get_json()
    # resolve primary options
    createtime = utils.currentTimeMillis()
    # resolve delay in seconds, if delay is negative it is reset to 0
    delay = utils.intOrElse(obj["delay"] if "delay" in obj else 0, 0)
    if delay < 0:
        delay = 0
    # resolve status based on delay
    status = Job.READY if delay == 0 else Job.DELAYED
    # resolve submit time (when job will be added to the queue)
    submittime = createtime + delay * 1000
    # resolve priority, if delay is 0 then priority is submittime else truncated submittime, so
    # delayed job can be scheduled as soon as possible once it is added to the queue
    priority = submittime if delay == 0 else submittime / 1000L
    # create (including validation and options parsing) Job instance
    job = Job.add(db, name=obj["name"], status=status, priority=priority, createtime=createtime,
        submittime=submittime, klass=obj["klass"], dmemory=obj["dmemory"], ememory=obj["ememory"],
        jar=obj["jar"], options=obj["sparkOptions"], jobconf=obj["jobOptions"])
    return success(job.json())

@app.route("/api/v1/template/list", methods=["GET"])
def template_list():
    templates = Template.list()
    return success({"templates": [x.json() for x in templates]})

@app.route("/api/v1/template/delete/<int:uid>", methods=["GET"])
def template_delete(uid):
    template = Template.get(uid)
    if not template:
        raise StandardError("No template for id '%s'" % uid)
    Template.delete(db, template)
    return success({"template": template.json()})

@app.route("/api/v1/template/delete_and_list/<int:uid>", methods=["GET"])
def template_delete_and_list(uid):
    template = Template.get(uid)
    if not template:
        raise StandardError("No template for id '%s'" % uid)
    Template.delete(db, template)
    return template_list()

@app.route("/api/v1/template/create", methods=["POST"])
def template_submit():
    opts = request.get_json()
    name = Template.getCanonicalName(opts["name"])
    content = json.dumps(opts)
    # construct template
    template = Template.add(db, name=name, createtime=utils.currentTimeMillis(), content=content)
    return success(template.json())
