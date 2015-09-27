#!/usr/bin/env python

import paths
import os
import sys
import urllib
from urlparse import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler

# process only API requests
class APICall(object):
    def __init__(self, path, query):
        self.path = path
        self.query = query

    def process(self):
        return {"code": 200, "content": "{\"name\": 1}"}

# process any other request with serving a file
class ServeCall(object):
    def __init__(self, path):
        self.path = path
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

# pages map for redirect
API_V1 = "/api/v1"
PAGE_MAP = {
    "": "index.html",
    "/": "index.html"
}
# root directory for http server
ROOT = paths.SERV_PATH

class SimpleHandler(BaseHTTPRequestHandler):
    def fullPath(self, path):
        path = path.lstrip("/")
        path = PAGE_MAP[path] if path in PAGE_MAP else path
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
            call = APICall(path, query)
            result = call.process()
            self.send_response(result["code"])
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(result["content"])
        else:
            call = ServeCall(path)
            # serve file
            try:
                with open(call.path) as f:
                    self.send_response(200)
                    self.send_header("Content-type", call.mimetype)
                    self.end_headers()
                    self.wfile.write(f.read())
            except IOError:
                self.send_error(404, "File Not Found: %s" % call.path)
