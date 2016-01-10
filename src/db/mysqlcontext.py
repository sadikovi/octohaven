#!/usr/bin/env python

import uuid
from contextlib import contextmanager
from mysql.connector import errorcode
from mysql.connector.errors import PoolError, Error as SQLGlobalError
from mysql.connector.pooling import MySQLConnectionPool
from octolog import Octolog

# `MySQLContext` is the main entry and wrapper to deal with storing and retrieving data from MySQL.
# It maintains connection pool and handles new connection allocations automatically.
# There is only one context per application, therefore should be created globally; it is not
# restricted currently, but will be added in the future.
class MySQLContext(Octolog, object):
    def __init__(self, **config):
        # min pool size, note that max size is 32
        min_pool_size = 2
        # default pool name
        default_pool_name = uuid.uuid4().hex
        if "pool_name" not in config:
            config["pool_name"] = default_pool_name
        if "pool_size" not in config:
            config["pool_size"] = min_pool_size
        else:
            config["pool_size"] = max(min_pool_size, config["pool_size"])
        # raise errors on warnings is true, since we want to capture any behaviour
        config["raise_on_warnings"] = True
        # instantiate pool
        self.logger().debug("Init pool %s with size %s", config["pool_name"], config["pool_size"])
        self.cnxpool = MySQLConnectionPool(**config)

    ############################################################
    # Connection handling
    ############################################################
    # Requiest existing or new connection from the pool
    def connection(self):
        conn = None
        try:
            conn = self.cnxpool.get_connection()
        except PoolError as pe:
            self.logger().debug("Failed to get free connection. Add new connection to the pool")
            self.cnxpool.add_connection()
            # new connection has been added
            self.logger().debug("Fetch newly added connection")
            conn = self.cnxpool.get_connection()
        return conn

    # Close all connections in the pool
    def closeAll(self):
        self.cnxpool._remove_connections()

    ############################################################
    # Transaction support
    ############################################################
    # Transaction support for sql connector, passes object "SQLAtomicOperations" as part of
    # "with clause":
    # ```
    # with sqlcon.transaction(ops):
    #   ops.insert(...)
    #   ops.insert(...)
    #   ops.update(...)
    # Everything within that clause will be executed as single transaction
    # Atomic operations must not be used within transactions, since they handle connections and
    # cursors, other resources automatically. Use provided SQLAtomicOperations object instead.
    @contextmanager
    def transaction(self):
        conn = self.connection()
        cursor = None
        operations = None
        try:
            cursor = conn.cursor(dictionary = True, buffered = True)
            operations = MySQLAtomicOperations(cursor)
            yield operations
        except SQLGlobalError as e:
            conn.rollback()
            self.logger().debug("Transaction failed with '%s'. Apply rollback", e.msg)
            raise e
        else:
            conn.commit()
        finally:
            if cursor:
                cursor.close()
            operations = None
            conn.close()
