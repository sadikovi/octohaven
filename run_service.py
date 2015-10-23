#!/usr/bin/env python

import paths
import sys
import time
from theserver import SimpleHandler, RichHTTPServer
from scheduler import Scheduler

# we require some parameters to be set up before running service
# this includes:
# 0. host, this will be "localhost" by default
# 1. port to run on, 33900 by default
# 2. Spark UI address, required (usually, it is http://localhost:8080)
# 3. Spark UI running address, required (usually, it is http://localhost:4040)
# 4. Spark master address, required (usually, it is spark://local:7077)
# 5. Jar folder, required (root folder for all .jar files, can have nested folders)
# 6. Redis host, default is localhost
# 7. Redis port, default is 6379
#
# split arguments and return pairs "key-value"
def pairs(args):
    for arg in args:
        arr = arg.split("=")
        if len(arr) != 2:
            print "[ERROR] Parameter %s cannot be parsed" % arg
            sys.exit(0)
        key, value = arr
        yield (key, value)

def getOrElse(params, key, default):
    return params[key] if key in params else default

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print """
Spark simple job server. Usage:
- run_service [OPTIONS]

Options are:
- host [ --host=localhost ]
- port [ --port=33900 ]
- (required) spark ui address [ --spark-ui-address=http://localhost:8080 ]
- (required) spark ui run address [ --spark-ui-run-address=http://localhost:4040 ]
- (required) spark master address [ --spark-master-address=spark://local:7077 ]
- (required) jar folder [ --jar-folder ]
- redis host [ --redis-host=localhost ]
- redis port [ --redis-port=6379 ]
- redis db [ --redis-db=11 ]

        """
        sys.exit(0)
    # map of parameters
    params = dict(pairs(args))
    # assign parameters
    host = getOrElse(params, "--host", "localhost")
    port = getOrElse(params, "--port", "33900")
    spark_ui_address = getOrElse(params, "--spark-ui-address", None)
    spark_ui_run_address = getOrElse(params, "--spark-ui-run-address", None)
    spark_master_address = getOrElse(params, "--spark-master-address", None)
    jar_folder = getOrElse(params, "--jar-folder", None)
    redis_host = getOrElse(params, "--redis-host", "localhost")
    redis_port = getOrElse(params, "--redis-port", "6379")
    redis_db = getOrElse(params, "--redis-db", "11")
    # check if any of required parameters are not set
    if not spark_ui_address:
        raise StandardError("Spark UI address must be set, e.g. http://localhost:8080")
    if not spark_ui_run_address:
        raise StandardError("Spark UI running address must be set, e.g. http://localhost:4040")
    if not spark_master_address:
        raise StandardError("Spark Master address must be set, e.g. spark://local:7077")
    if not jar_folder:
        raise StandardError("Jar folder must be set and be a valid directory")

    # global settings necessary to run application
    settings = {
        "SPARK_UI_ADDRESS": spark_ui_address,
        "SPARK_UI_RUN_ADDRESS": spark_ui_run_address,
        "SPARK_MASTER_ADDRESS": spark_master_address,
        "JAR_FOLDER": jar_folder,
        "REDIS_HOST": redis_host,
        "REDIS_PORT": redis_port,
        "REDIS_DB": redis_db
    }

    # prepare server
    server = RichHTTPServer
    httpd = server(host, int(port), SimpleHandler, settings)
    # prepare scheduler
    # scheduler = Scheduler(settings)

    print "[INFO] Spark UI address is set to %s" % spark_ui_address
    print "[INFO] Spark UI run address is set to %s" % spark_ui_run_address
    print "[INFO] Spark Master address is set to %s" % spark_master_address
    print "[INFO] Jar folder is set to %s" % jar_folder
    print "[INFO] Redis host and port are set to %s:%s" % (redis_host, redis_port)
    print "[INFO] Using Redis db %s" % redis_db
    print "[INFO] Starting up scheduler"
    # scheduler.run()
    print time.asctime(), "Serving HTTP on %s:%s ..." % (host, port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        # scheduler.stop()
        print "Stop scheduler"
        httpd.server_close()
        print time.asctime(), "Stop serving on %s:%s ..." % (host, port)
