#!/usr/bin/env python

import paths
import os
import sys
import urllib
import json
from urlparse import urlparse
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import sparkheartbeat
from redisconnector import RedisConnector, RedisConnectionPool
from storagemanager import StorageManager

# constants for request mapping
API_V1 = "/api/v1"
REQUEST_TABLE = {
    "": "index.html",
    "/": "index.html",
    "create": "create.html"
}
# root directory for http server
ROOT = paths.SERV_PATH

# process only API requests
class APICall(object):
    def __init__(self, path, query, settings):
        self.path = path
        self.query = query
        self.settings = settings
        # check Spark settings
        if "SPARK_UI_ADDRESS" not in self.settings or "SPARK_MASTER_ADDRESS" not in self.settings:
            raise StandardError("Spark UI Address and Spark Master Address must be specified")
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

    def process(self):
        try:
            if self.path.endswith("%s/sparkstatus" % API_V1):
                # call Spark heartbeat
                status = sparkheartbeat.sparkStatus(self.settings["SPARK_UI_ADDRESS"])
                return {"code": 200, "status": "OK", "content": {
                    "sparkstatus": status,
                    "spark-ui-address": self.settings["SPARK_UI_ADDRESS"],
                    "spark-master-address": self.settings["SPARK_MASTER_ADDRESS"]
                }}
            elif self.path.endswith("%s/jobs" % API_V1):
                # retrieve jobs for status
                # we are expecting one parameter starting with "status="
                pairs = [q.split("=", 1) for q in self.query if q.startswith("status")]
                if len(pairs) == 1 and len(pairs[0]) == 2:
                    status = pairs[0][1]
                    jobs = self.storageManager.jobsForStatus(status)
                    return {"code": 200, "status": "OK", "content": {
                        "jobs": [job.toDict() for job in jobs]
                    }}
                else:
                    # raise error
                    return {"code": 400, "status": "ERROR", "content": {
                        "msg": "expected one 'status' parameter"
                    }}
            elif self.path.endswith("%s/test/populate" % API_V1):
                # TEST API (will go away eventually)
                # clear db and add some dummy records
                self.storageManager.connector.flushdb()
                def newJob(index):
                    import uuid, time, random
                    from job import Job, STATUSES
                    uid = str(uuid.uuid4())
                    status = random.choice(STATUSES)
                    starttime = long(time.time())
                    name = "Test job for index %d" % index
                    duration = "MEDIUM"
                    command = "spark-submit test command"
                    return Job(uid, status, starttime, name, duration, command)
                jobs = [newJob(i) for i in range(30)]
                for job in jobs:
                    self.storageManager.addJobForStatus(self.storageManager.ALL_JOBS_KEY, job.uid)
                    self.storageManager.addJobForStatus(job.status, job.uid)
                    self.storageManager.saveJob(job)
        except BaseException as e:
            return {"code": 400, "status": "ERROR", "content": {"msg": e.message}}
        else:
            return {"code": 200, "content": {}}

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

# creates updated version of HTTPServer with settings
class RichHTTPServer(HTTPServer):
    def __init__(self, host, port, handler, settings):
        self.settings = settings
        HTTPServer.__init__(self, (host, port), handler)
