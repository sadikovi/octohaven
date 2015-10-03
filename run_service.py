#!/usr/bin/env python

import paths
import sys
import time
from theserver import SimpleHandler, RichHTTPServer

# we require some parameters to be set up before running service
# this includes:
# 0. host, this will be "localhost" by default
# 1. port to run on, 33900 by default
# 2. Spark UI address, required (usually, it is http://localhost:8080)
# 3. Spark master address, required (usually, it is spark://local:7077)
# 4. Redis host, default is localhost
# 5. Redis port, default is 6379
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
- (required) spark master address [ --spark-master-address=spark://local:7077 ]
- redis host [ --redis-host=localhost ]
- redis port [ --redis-port=6379 ]
- redis db [ --redis-db=11 ]

        """
        sys.exit(0)
    # map of parameters
    params = dict(pairs(args))
    # assign parameters
    host = params["--host"] if "--host" in params else "localhost"
    port = params["--port"] if "--port" in params else "33900"
    spark_ui_address = params["--spark-ui-address"] if "--spark-ui-address" in params else None
    spark_master_address = params["--spark-master-address"] if "--spark-master-address" in params else None
    redis_host = params["--redis-host"] if "--redis-host" in params else "localhost"
    redis_port = params["--redis-port"] if "--redis-port" in params else "6379"
    redis_db = params["--redis-db"] if "--redis-db" in params else "11"
    # check if any of required parameters are not set
    if spark_ui_address is None:
        raise StandardError("Spark UI address must be set, e.g. http://localhost:8080")
    if spark_master_address is None:
        raise StandardError("Spark Master address must be set, e.g. spark://local:7077")

    server = RichHTTPServer
    httpd = server(host, int(port), SimpleHandler, {
        "SPARK_UI_ADDRESS": spark_ui_address,
        "SPARK_MASTER_ADDRESS": spark_master_address,
        "REDIS_HOST": redis_host,
        "REDIS_PORT": redis_port,
        "REDIS_DB": redis_db
    })

    print "[INFO] Spark UI address is set to %s" % spark_ui_address
    print "[INFO] Spark Master address is set to %s" % spark_master_address
    print "[INFO] Redis host and port are set to %s:%s" % (redis_host, redis_port)
    print "[INFO] Using Redis db %s" % redis_db
    print time.asctime(), "Serving HTTP on %s:%s ..." % (host, port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print time.asctime(), "Stop serving on %s:%s ..." % (host, port)
