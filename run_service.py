#!/usr/bin/env python

import paths
import sys
import time
from BaseHTTPServer import HTTPServer
from theserver import SimpleHandler

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args: raise StandardError("HTTP port is required")
    host = "localhost"
    port = int(args[0])
    server = HTTPServer
    httpd = server((host, port), SimpleHandler)
    print time.asctime(), "Serving HTTP on %s port %s ..." % (host, port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print time.asctime(), "Stop serving on %s port %s ..." % (host, port)
