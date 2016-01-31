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

from flask import Flask, redirect, render_template, make_response, jsonify, abort, url_for
from config import VERSION
from extlogging import Loggable
from sparkmodule import SparkContext
from sqlmodule import MySQLContext
from sqlschema import loadSchema
from fs import FileManager

################################################################
# Application setup
################################################################
app = Flask("octohaven")
app.config.from_object("config.TestConfig")
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
sqlContext = MySQLContext(host=app.config["MYSQL_HOST"], port=app.config["MYSQL_PORT"],
    database=app.config["MYSQL_DATABASE"], user=app.config["MYSQL_USER"],
    password=app.config["MYSQL_PASSWORD"], pool_size=10)
# Check database schema to make sure that we have all tables to continue
loadSchema(sqlContext, app.config["MYSQL_SCHEMA_RESET"])

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

@app.route("/")
def index():
    return redirect("/jobs/all")

@app.route("/jobs")
def jobs():
    return redirect("/jobs/all")

@app.route("/jobs/<status>")
def jobs_for_status(status):
    status = str(status).upper()
    statuses = ["ALL", "READY", "DELAYED", "RUNNING", "FINISHED", "CLOSED"]
    if status not in statuses:
        status = "ALL"
    return render_page("jobs.html", status=status, statuses=statuses)

@app.route("/create/<entity>")
def create(entity):
    entity = str(entity).lower()
    if entity == "job":
        # redirect to the page of creating a job
        return render_page("create_job.html")
    elif entity == "timetable":
        return abort(404)
    else:
        return abort(404)

################################################################
# REST API
################################################################
# successful response helper
def success(payload):
    return make_response(jsonify({"code": 200, "payload": payload}), 200)

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
