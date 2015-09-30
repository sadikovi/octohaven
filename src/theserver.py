#!/usr/bin/env python

import paths
import os
import sys
import urllib
import json
from urlparse import urlparse
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import sparkheartbeat
# constants for request mapping
API_V1 = "/api/v1"
REQUEST_TABLE = {
    "": "index.html",
    "/": "index.html"
}
# root directory for http server
ROOT = paths.SERV_PATH

# process only API requests
class APICall(object):
    def __init__(self, path, query, settings):
        self.path = path
        self.query = query
        self.settings = settings
        if "SPARK_UI_ADDRESS" not in self.settings or "SPARK_MASTER_ADDRESS" not in self.settings:
            raise StandardError("Spark UI Address and Spark Master Address must be specified")

    def process(self):
        if self.path.endswith("%s/sparkstatus" % API_V1):
            # call Spark heartbeat
            try:
                status = sparkheartbeat.sparkStatus(self.settings["SPARK_UI_ADDRESS"])
                return {"code": 200, "status": "OK", "content": {
                    "sparkstatus": status,
                    "spark-ui-address": self.settings["SPARK_UI_ADDRESS"],
                    "spark-master-address": self.settings["SPARK_MASTER_ADDRESS"]
                }}
            except BaseException as e:
                return {"code": 400, "status": "ERROR", "content": {"msg": e.message}}
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
