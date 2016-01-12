#!/usr/bin/env python

import sys, unittest, paths
from cli import CLI
from src.octo.mysqlcontext import MySQLContext
from src.octo.storagesetup import loadTables

if __name__ == '__main__':
    cli = CLI(sys.argv[1:])
    config = {
        "host": cli.get("host"),
        "port": cli.get("port"),
        "user": cli.get("user"),
        "password": cli.get("password"),
        "database": cli.get("database")
    }

    # sanity check of parameters
    for key, value in config.items():
        if not value:
            print "[ERROR] Option '%s' is not specified. " % key + \
                "Required 'host', 'port', 'user', 'password', 'database' to connect to DB. " + \
                "E.g. python run_setup.py host=localhost port=3306 user=u1 password=p1 database=d1"
            sys.exit(1)

    # other options
    drop_existing = cli.get("drop_existing")

    print "[INFO] Setup MySQL instance..."
    print "[INFO] Using configuration:"
    print " host: %s" % config["host"]
    print " port: %s" % config["port"]
    print " user: %s" % config["user"]
    print " password: %s" % "*****"
    print " database: %s" % config["database"]

    sqlcnx = MySQLContext(**config)
    loadTables(sqlcnx, drop_existing, logging=True)
    print "[INFO] Done"
