#!/usr/bin/env python

import paths
import os, sys, urllib, json
from urlparse import urlparse
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import sparkheartbeat
from redisconnector import RedisConnector, RedisConnectionPool
from storagemanager import StorageManager
from filemanager import FileManager
from jobmanager import JobManager
from job import Job, SparkJob
from utils import *

# constants for request mapping
API_V1 = "/api/v1"
REQUEST_TABLE = {
    "": "index.html",
    "/": "index.html",
    "create": "create.html",
    "job": "job.html"
}
# root directory for http server
ROOT = paths.SERV_PATH

# process only API requests
class APICall(object):
    def __init__(self, path, query, settings):
        self.path = path
        # query is a key-value map
        self.query = dict([pair for pair in [q.split("=", 1) for q in query] if len(pair) == 2])
        self.settings = settings
        # check Spark settings
        if "SPARK_UI_ADDRESS" not in self.settings or "SPARK_MASTER_ADDRESS" not in self.settings:
            raise StandardError("Spark UI Address and Spark Master Address must be specified")
        sparkMasterAddress = settings["SPARK_MASTER_ADDRESS"]
        # check whether Jar folder is set
        if "JAR_FOLDER" not in self.settings:
            raise StandardError("Jar folder is not set")
        jarFolder = self.settings["JAR_FOLDER"]
        # make connection to Redis
        if "REDIS_HOST" not in self.settings or "REDIS_PORT" not in self.settings \
            or "REDIS_DB" not in self.settings:
            raise StandardError("Redis host, port and db must be specified")
        pool = RedisConnectionPool({
            "host": self.settings["REDIS_HOST"],
            "port": int(self.settings["REDIS_PORT"]),
            "db": int(self.settings["REDIS_DB"])
        })
        connector = RedisConnector(pool)
        self.storageManager = StorageManager(connector)
        self.fileManager = FileManager(jarFolder)
        self.jobManager = JobManager(sparkMasterAddress)
        self.response = None

    @private
    def sendError(self, msg=""):
        self.response = {"code": 400, "status": "ERROR", "content": {"msg": "%s" % msg}}

    @private
    def sendSystemError(self, msg=""):
        self.response = {"code": 500, "status": "ERROR", "content": {"msg": "%s" % msg}}

    @private
    def sendSuccess(self, content):
        self.response = {"code": 200, "status": "OK", "content": content}

    # process method for different API methods:
    # - GET /api/v1/sparkstatus: fetching Spark cluster status
    # - GET /api/v1/jobs: listing jobs for a status
    # - GET /api/v1/job: fetch job for an id
    # - POST /api/v1/submit: create a new job
    # - GET /api/v1/close: close existing job, if possible
    # - GET /api/v1/breadcrumbs: list a directory traversal for a specific path
    # - GET /api/v1/list: list folders and files for a specific path
    def process(self):
        try:
            if self.path.endswith("%s/sparkstatus" % API_V1):
                # call Spark heartbeat
                status = sparkheartbeat.sparkStatus(self.settings["SPARK_UI_ADDRESS"])
                self.sendSuccess({
                    "sparkstatus": status,
                    "spark-ui-address": self.settings["SPARK_UI_ADDRESS"],
                    "spark-master-address": self.settings["SPARK_MASTER_ADDRESS"]
                })
            elif self.path.endswith("%s/jobs" % API_V1):
                # retrieve jobs for status
                # we are expecting one parameter starting with "status="
                if "status" in self.query:
                    limit = intOrElse(self.query["limit"], -1) if "limit" in self.query else None
                    sort = boolOrElse(self.query["sort"], True) if "sort" in self.query else None
                    status = self.query["status"]
                    jobs = self.storageManager.jobsForStatus(status, limit, sort)
                    self.sendSuccess({"jobs": [job.toDict() for job in jobs]})
                else:
                    self.sendError("expected 'status' parameter")
            elif self.path.endswith("%s/job" % API_V1):
                # get job for id
                jobid = self.query["jobid"] if "jobid" in self.query else None
                job = self.storageManager.jobForUid(jobid)
                if not job:
                    self.sendError("No job found for id: %s" % str(jobid))
                else:
                    self.sendSuccess({"job": job.toDict()})
            elif self.path.endswith("%s/submit" % API_V1):
                # submit a new job
                if "content" not in self.query or not self.query["content"]:
                    self.sendError("Job information expected, got empty input")
                else:
                    raw = self.query["content"].strip()
                    # resolve and validate some of the parameters
                    # create job and store it using StorageManager
                    data = jsonOrElse(raw, None)
                    if not data:
                        raise StandardError("Corrupt json data: " + raw)
                    name = data["name"]
                    entry = data["mainClass"]
                    dmem, emem = data["driverMemory"], data["executorMemory"]
                    options = data["options"]
                    jar = self.fileManager.resolveRelativePath(data["jar"])
                    # job specific configuration options
                    jobconf = data["jobconf"]
                    # delay for a job to schedule, in seconds
                    delay = int(data["delay"]) if "delay" in data else 0
                    # create Spark job and octohaven job
                    sparkjob = self.jobManager.createSparkJob(
                        name, entry, jar, dmem, emem, options, jobconf)
                    job = self.jobManager.createJob(sparkjob, delay)
                    # save and register job in Redis for a status
                    self.storageManager.registerJob(job)
                    # all is good, send back job id to track
                    self.sendSuccess({"msg": "Job has been created", "jobid": job.uid})
            elif self.path.endswith("%s/close" % API_V1):
                # close a job
                jobid = self.query["jobid"] if "jobid" in self.query else None
                job = self.storageManager.jobForUid(jobid)
                if not job:
                    self.sendError("No job found for id: %s" % str(jobid))
                else:
                    # change status on "Closed", it will raise an error, if something is wrong
                    self.storageManager.unregisterJob(job, save=False)
                    self.jobManager.closeJob(job)
                    self.storageManager.registerJob(job)
                    self.sendSuccess({"msg": "Job has been updated", "jobid": job.uid})
            elif self.path.endswith("%s/breadcrumbs" % API_V1):
                # return breadcrumbs for a path
                path = self.query["path"] if "path" in self.query else ""
                data = self.fileManager.breadcrumbs(path, asdict=True)
                self.sendSuccess({"breadcrumbs": data})
            elif self.path.endswith("%s/list" % API_V1):
                # list folders and files for a path
                path = self.query["path"] if "path" in self.query else ""
                data = self.fileManager.list(path, sort=True, asdict=True)
                self.sendSuccess({"list": data})
            # if there is no reponse by the end of the block, we raise an error, as response was not
            # prepared for user or there were holes in logic flow
            if not self.response:
                raise Exception("Response could not be created")
        except StandardError as e:
            self.sendError(e.message)
        except BaseException as e:
            self.sendSystemError(e.message)
        # return final response
        return self.response

# process any other request with serving a file
class ServeCall(object):
    def __init__(self, path, settings):
        self.path = path
        self.settings = settings
        self.mimetype = self.mimetype(path)

    def mimetype(self, path):
        if path.endswith(".html"):
            return "text/html"
        elif path.endswith(".js"):
            return "application/javascript"
        elif path.endswith(".css"):
            return "text/css"
        else:
            return "text/plain"

class SimpleHandler(BaseHTTPRequestHandler):
    def fullPath(self, path):
        path = path.lstrip("/")
        path = REQUEST_TABLE[path] if path in REQUEST_TABLE else path
        return os.path.join(ROOT, path)

    def do_GET(self):
        # get parsed object to extract path and query parameters
        parsed = urlparse(self.path)
        isapi = self.path.startswith(API_V1)
        path = self.fullPath(urllib.unquote(parsed.path))
        query = [urllib.unquote(part) for part in parsed.query.split("&")]
        self.log_message("Requested %s" % path)
        self.log_message("Received query %s" % query)
        # parsing requested file
        if isapi:
            # process this as api request
            call = APICall(path, query, self.server.settings)
            result = call.process()
            self.send_response(result["code"])
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result))
        else:
            call = ServeCall(path, self.server.settings)
            # serve file
            try:
                with open(call.path) as f:
                    self.send_response(200)
                    self.send_header("Content-type", call.mimetype)
                    self.end_headers()
                    self.wfile.write(f.read())
            except IOError:
                self.send_error(404, "File Not Found: %s" % call.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        isapi = self.path.startswith(API_V1)
        path = self.fullPath(urllib.unquote(parsed.path))
        self.log_message("Requested %s" % path)
        if isapi:
            # process api request
            # get content in bytes
            content = self.headers.getheader("Content-Length")
            self.log_message("Content received: %s" % (content is not None))
            # raw string content
            raw = self.rfile.read(int(content) if content else 0)
            self.log_message("Raw content is %s" % raw)
            # in case of POST query is a list with one element which is unquoted raw string that
            # can be a json or xml, etc.
            query = ["content=%s" % urllib.unquote(raw)]
            call = APICall(path, query, self.server.settings)
            result = call.process()
            # as with GET, POST api returns json
            self.send_response(result["code"])
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result))
        else:
            # fail, as we do not process POST requests for non-api tasks
            self.send_error(400, "POST is not supported for general queries")

# creates updated version of HTTPServer with settings
class RichHTTPServer(HTTPServer):
    def __init__(self, host, port, handler, settings):
        self.settings = settings
        HTTPServer.__init__(self, (host, port), handler)
