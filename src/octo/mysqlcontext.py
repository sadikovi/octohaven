#!/usr/bin/env python

import uuid
from contextlib import contextmanager
from mysql.connector import errorcode
from mysql.connector.errors import PoolError, Error as SQLGlobalError
from mysql.connector.pooling import MySQLConnectionPool
from octolog import Octolog

# [OCTO-57] keep track of number of instances of MySQLContext. Currently allow only one instance
# per application.
class MySQLLock(Octolog, object):
    # maximum contexts
    MAX_ALLOWERD_NUM_INSTANCES = 1
    # current number of contexts
    MYSQLCONTEXT_NUM_INSTANCES = 0

    @classmethod
    def incrementNum(cls):
        cls.MYSQLCONTEXT_NUM_INSTANCES = cls.MYSQLCONTEXT_NUM_INSTANCES + 1

    @classmethod
    def validateLock(cls):
        if cls.MYSQLCONTEXT_NUM_INSTANCES + 1 > cls.MAX_ALLOWERD_NUM_INSTANCES:
            raise StandardError("Cannot instantiate MySQLContext, " +
                "only %s contexts are allowed per application" % cls.MAX_ALLOWERD_NUM_INSTANCES)

    # method for testing only
    @classmethod
    def reset(cls):
        cls.MYSQLCONTEXT_NUM_INSTANCES = 0

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
        # check that instantiation of sql context is within required bound
        MySQLLock.validateLock()
        MySQLLock.incrementNum()

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
    # Transaction support for sql connector, passes cursor as part of "with clause":
    # ```
    # with sqlcon.cursor(with_transaction = True) as cr:
    #   ...
    #   cr.execute(sql, args)
    # ```
    # Everything within that clause will be executed as single block, and as transaction, if
    # "with_transaction" is set to True.
    @contextmanager
    def cursor(self, with_transaction=True):
        conn = self.connection()
        cursor = None
        operations = None
        try:
            cursor = conn.cursor(dictionary = True, buffered = True)
            yield cursor
        except SQLGlobalError as e:
            if with_transaction:
                conn.rollback()
                self.logger().debug("Transaction failed with '%s'. Apply rollback", e.msg)
            raise e
        else:
            if with_transaction:
                conn.commit()
        finally:
            if cursor:
                cursor.close()
            operations = None
            conn.close()

    ############################################################
    # DDL atomic operations
    ############################################################
    def truncateTable(self, tableName):
        with self.cursor(with_transaction=False) as cr:
            ddl = "TRUNCATE TABLE `%s`" % tableName
            cr.execute(ddl)
        return True

    def dropTable(self, tableName):
        status = True
        with self.cursor(with_transaction=False) as cr:
            ddl = "DROP TABLE IF EXISTS `%s`" % tableName
            try:
                cr.execute(ddl)
            except SQLGlobalError as err:
                if err.errno == errorcode.ER_BAD_TABLE_ERROR:
                    status = False
                else:
                    raise err
        return status

    def createTable(self, ddl):
        status = True
        with self.cursor(with_transaction=False) as cr:
            try:
                cr.execute(ddl)
            except SQLGlobalError as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    status = False
                else:
                    raise err
        return status
