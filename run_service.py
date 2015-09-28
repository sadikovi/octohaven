#!/usr/bin/env python

import paths
import sys
import time
from theserver import SimpleHandler, RichHTTPServer

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args or len(args) < 3:
        raise StandardError("Parameters required: HTTP port, Spark UI URL, Spark Master URL")
    host = ""
    port = int(args[0])
    SPARK_UI_ADDRESS = args[1]
    SPARK_MASTER_ADDRESS = args[2]
    server = RichHTTPServer
    httpd = server(host, port, SimpleHandler, {
        "SPARK_UI_ADDRESS": SPARK_UI_ADDRESS,
        "SPARK_MASTER_ADDRESS": SPARK_MASTER_ADDRESS
    })
    print time.asctime(), "Serving HTTP on %s port %s ..." % (host, port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print time.asctime(), "Stop serving on %s port %s ..." % (host, port)
