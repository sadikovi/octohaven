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
app_log.logger.info("MySQL connection - password - %s" % app.config["MYSQL_PASSWORD"][:3] + "***")

# Spark module is one per application, currently UI Run address is not supported, so we pass UI
# address as dummy value
sparkContext = SparkContext(app.config["SPARK_MASTER_ADDRESS"], app.config["SPARK_UI_ADDRESS"],
    app.config["SPARK_UI_ADDRESS"])
# SQL context is one per application
sqlContext = MySQLContext(host=app.config["MYSQL_HOST"], port=app.config["MYSQL_PORT"],
    database=app.config["MYSQL_DATABASE"], user=app.config["MYSQL_USER"],
    password=app.config["MYSQL_PASSWORD"], pool_size=10)

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
    else:
        return abort(404)

################################################################
# REST API
################################################################
# successful response helper
def success(payload, code=200):
    return make_response(jsonify({"code": code, "payload": payload}), code)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({"code": 400, "msg": "Bad request"}), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"code": 404, "msg": "Not found"}), 404)

@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({"code": 500, "msg": "Internal error"}), 500)

@app.route("/api/v1/spark/status", methods=["GET"])
def spark_status():
    status = sparkContext.clusterStatus()
    return success({"status": status})
