#!/usr/bin/env python

import paths
import os, sys, urllib, json
from urlparse import urlparse
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from redisconnector import RedisConnector, RedisConnectionPool
from storagemanager import StorageManager
from filemanager import FileManager
from jobmanager import JobManager
from job import Job, SparkJob
from sparkmodule import SparkModule
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
        if "SPARK_UI_ADDRESS" not in self.settings:
            raise StandardError("Spark UI Address is not specified")
        if "SPARK_UI_RUN_ADDRESS" not in self.settings:
            raise StandardError("Spark UI Address for running applications is not specified")
        if "SPARK_MASTER_ADDRESS" not in self.settings:
            raise StandardError("Spark Master Address is not specified")
        sparkUi = settings["SPARK_UI_ADDRESS"]
        sparkUiRun = settings["SPARK_UI_RUN_ADDRESS"]
        sparkMaster = settings["SPARK_MASTER_ADDRESS"]
        # check whether Jar folder is set
        if "JAR_FOLDER" not in self.settings:
            raise StandardError("Jar folder is not set")
        jarFolder = self.settings["JAR_FOLDER"]
        # make connection to Redis
        if "REDIS_HOST" not in self.settings:
            raise StandardError("Redis host is not specified")
        if "REDIS_PORT" not in self.settings:
            raise StandardError("Redis port is not specified")
        if "REDIS_DB" not in self.settings:
            raise StandardError("Redis db is not specified")
        pool = RedisConnectionPool({
            "host": self.settings["REDIS_HOST"],
            "port": int(self.settings["REDIS_PORT"]),
            "db": int(self.settings["REDIS_DB"])
        })
        connector = RedisConnector(pool)
        storageManager = StorageManager(connector)
        self.sparkModule = SparkModule(sparkMaster, sparkUi, sparkUiRun)
        self.fileManager = FileManager(jarFolder)
        self.jobManager = JobManager(self.sparkModule, storageManager)
        self.response = None

    @private
    def error(self, msg=""):
        return {"code": 400, "status": "ERROR", "content": {"msg": "%s" % msg}}

    @private
    def systemError(self, msg=""):
        return {"code": 500, "status": "ERROR", "content": {"msg": "%s" % msg}}

    @private
    def success(self, content):
        return {"code": 200, "status": "OK", "content": content}

    # process method for different API methods:
    # - GET     /api/v1/spark/status: fetching Spark cluster status
    # - GET     /api/v1/jobs/list: listing jobs for a status
    # - GET     /api/v1/job/get: fetch job for an id
    # - POST    /api/v1/job/submit: create a new job
    # - GET     /api/v1/job/close: close existing job, if possible
    # - GET     /api/v1/files/breadcrumbs: list a directory traversal for a specific path
    # - GET     /api/v1/files/list: list folders and files for a specific path
    def process(self):
        try:
            # list of API functions, see comment above. Everything is called in if-else statement
            # that decides what response to send. If API is undefined we raise a system error 500

            def sparkStatus():
                status = self.sparkModule.clusterStatus()
                return self.success({
                    "status": status,
                    "spark-ui-address": self.sparkModule.uiAddress,
                    "spark-master-address": self.sparkModule.masterAddress
                })

            def jobsList():
                if "status" not in self.query:
                    raise StandardError("Expected 'status' parameter")
                status = self.query["status"]
                limit = intOrElse(self.query["limit"], -1) if "limit" in self.query else -1
                sort = boolOrElse(self.query["sort"], True) if "sort" in self.query else True
                jobs = self.jobManager.listJobsForStatus(status, limit, sort)
                return self.success({"jobs": [job.toDict() for job in jobs]})

            def jobGet():
                jobid = self.query["jobid"] if "jobid" in self.query else None
                job = self.jobManager.jobForUid(jobid)
                if not job:
                    raise StandardError("No job found for 'jobid': %s" % str(jobid))
                return self.success({"job": job.toDict()})

            def jobSubmit():
                # submit a new job
                if "content" not in self.query or not self.query["content"]:
                    raise StandardError("Job information expected, got empty input")
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
                sparkjob = self.jobManager.createSparkJob(name, entry, jar, dmem, emem, options,
                    jobconf)
                job = self.jobManager.createJob(sparkjob, delay)
                # save and register job in Redis for a status
                self.jobManager.saveJob(job)
                # all is good, send back job id to track
                return self.success({"msg": "Job has been created", "jobid": job.uid})

            def jobClose():
                jobid = self.query["jobid"] if "jobid" in self.query else None
                job = self.storageManager.jobForUid(jobid)
                if not job:
                    raise StandardError("No job found for 'jobid': %s" % str(jobid))
                self.jobManager.closeJob(job)
                return self.success({"msg": "Job has been closed", "jobid": job.uid})

            def filesBreadcrumbs():
                # return breadcrumbs for a path
                path = self.query["path"] if "path" in self.query else ""
                data = self.fileManager.breadcrumbs(path, asdict=True)
                return self.success({"breadcrumbs": data})

            def filesList():
                # list folders and files for a path
                path = self.query["path"] if "path" in self.query else ""
                data = self.fileManager.list(path, sort=True, asdict=True)
                return self.success({"list": data})

            if self.path.endswith("%s/spark/status" % API_V1):
                self.response = sparkStatus()
            elif self.path.endswith("%s/jobs/list" % API_V1):
                self.response = jobsList()
            elif self.path.endswith("%s/job/get" % API_V1):
                self.response = jobGet()
            elif self.path.endswith("%s/job/submit" % API_V1):
                self.response = jobSubmit()
            elif self.path.endswith("%s/job/close" % API_V1):
                self.response = jobClose()
            elif self.path.endswith("%s/files/breadcrumbs" % API_V1):
                self.response = filesBreadcrumbs()
            elif self.path.endswith("%s/files/list" % API_V1):
                self.response = filesList()
            else:
                # API does not exist for the type of the query
                raise Exception("No API for the query: %s" % self.path)
        except StandardError as e:
            self.response = self.error(e.message)
        except BaseException as e:
            self.response = self.systemError(e.message)
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
