#!/usr/bin/env python

import unittest, test, mysql
from src.db.mysqlcontext import MySQLContext
from mysql.connector.errors import PoolError, Error as SQLGlobalError
from utils import *

class MySQLContextTestSuite(unittest.TestCase):
    def setUp(self):
        self.config = {
            "host": test.Settings.mp().get("host"),
            "port": test.Settings.mp().get("port"),
            "user": test.Settings.mp().get("user"),
            "password": test.Settings.mp().get("password"),
            "database": test.Settings.mp().get("database")
        }
        # test table
        self.table = "test"
        self.ddl = (
            "create table if not exists test ("
            "   uid int unsigned auto_increment primary key,"
            "   name varchar(255),"
            "   createtime bigint unsigned"
            ") engine = InnoDB"
        )

    def tearDown(self):
        pass

    def test_init(self):
        sqlcnx = MySQLContext(**self.config)
        self.assertEqual(len(sqlcnx.cnxpool.pool_name), 32)
        self.assertEqual(sqlcnx.cnxpool.pool_size, 2)
        # init specific name and pool size
        self.config["pool_name"] = "dummy"
        self.config["pool_size"] = 10
        sqlcnx = MySQLContext(**self.config)
        self.assertEqual(sqlcnx.cnxpool.pool_name, self.config["pool_name"])
        self.assertEqual(sqlcnx.cnxpool.pool_size, self.config["pool_size"])

    def test_connection(self):
        sqlcnx = MySQLContext(**self.config)
        # create first connection
        conn1 = sqlcnx.connection()
        self.assertNotEqual(conn1, None)
        conn1.ping()
        # create second connection
        conn2 = sqlcnx.connection()
        self.assertNotEqual(conn2, None)
        conn2.ping()
        # create third connection (should not fail)
        conn3 = sqlcnx.connection()
        self.assertNotEqual(conn3, None)
        conn3.ping()
        # close all connections
        sqlcnx.closeAll()

    def test_connection_closeall(self):
        sqlcnx = MySQLContext(**self.config)
        # create first connection
        conn1 = sqlcnx.connection()
        conn2 = sqlcnx.connection()
        # after closing all connections we will be able assign conn3 and conn4
        sqlcnx.closeAll()
        conn3 = sqlcnx.connection()
        conn3.ping()
        conn4 = sqlcnx.connection()
        conn4.ping()
        # close all connections
        sqlcnx.closeAll()

    def test_insert(self):
        sqlcnx = MySQLContext(**self.config)
        sqlcnx.dropTable(self.table)
        sqlcnx.createTable(self.ddl)
        uid = None
        with sqlcnx.transaction() as ops:
            uid = ops.insert(self.table, **{"name": "a", "createtime": 123})
        rows = sqlcnx.select(self.table, 1, **{"uid": uid})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["uid"], uid)
        self.assertEqual(rows[0]["name"], "a")
        self.assertEqual(rows[0]["createtime"], 123)
        # test failed transaction
        with self.assertRaises(StandardError):
            with sqlcnx.transactions() as ops:
                uid = ops.insert(self.table, **{"name": "a", "createtime": 123})
                raise StandardError()
        rows = sqlcnx.select(self.table, -1)
        self.assertEqual(len(rows), 1)

    def test_update(self):
        sqlcnx = MySQLContext(**self.config)
        sqlcnx.dropTable(self.table)
        sqlcnx.createTable(self.ddl)
        uid = None
        with sqlcnx.transaction() as ops:
            uid = ops.insert(self.table, **{"name": "a", "createtime": 123})
            ops.update(self.table, **{"name": "b", "createtime": 124, "uid": uid})
        rows = sqlcnx.select(self.table, 1, **{"uid": uid})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["uid"], uid)
        self.assertEqual(rows[0]["name"], "b")
        self.assertEqual(rows[0]["createtime"], 124)
        # test update without uid
        with self.assertRaises(StandardError):
            ops.update(self.table, **{"name": "b", "createtime": 124})

    def test_delete(self):
        sqlcnx = MySQLContext(**self.config)
        sqlcnx.dropTable(self.table)
        sqlcnx.createTable(self.ddl)
        uid = None
        with sqlcnx.transaction() as ops:
            uid = ops.insert(self.table, **{"name": "a", "createtime": 123})
            ops.delete(self.table, **{"uid": uid})
        rows = sqlcnx.select(self.table, 1, **{"uid": uid})
        self.assertTrue(not rows)

    def test_atomic_operations(self):
        sqlcnx = MySQLContext(**self.config)
        sqlcnx.dropTable(self.table)
        sqlcnx.createTable(self.ddl)
        uid = sqlcnx.insert(self.table, **{"name": "test1", "createtime": 1})
        sqlcnx.update(self.table, **{"name": "test2", "createtime": 2, "uid": uid})
        rows = sqlcnx.select(self.table, 1, **{"uid": uid})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["uid"], uid)
        self.assertEqual(rows[0]["name"], "test2")
        self.assertEqual(rows[0]["createtime"], 2)
        # test failure
        uid = sqlcnx.insert(self.table, **{"name": "test3", "createtime": 3})
        with self.assertRaises(SQLGlobalError):
            sqlcnx.update(self.table, **{"name": "test2", "createtime": "test", "uid": uid})
        rows = sqlcnx.select(self.table, -1)
        # check that row has been inserted
        self.assertEqual(len(rows), 2)

    def test_transaction(self):
        sqlcnx = MySQLContext(**self.config)
        sqlcnx.dropTable(self.table)
        sqlcnx.createTable(self.ddl)
        with sqlcnx.transaction() as ops:
            uid = ops.insert(self.table, **{"name": "test1", "createtime": 1})
            ops.update(self.table, **{"name": "test2", "createtime": 2, "uid": uid})
        rows = sqlcnx.select(self.table, 1, **{"uid": uid})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["uid"], uid)
        self.assertEqual(rows[0]["name"], "test2")
        self.assertEqual(rows[0]["createtime"], 2)
        # test failure, should rollback inserted records
        with self.assertRaises(SQLGlobalError):
            with sqlcnx.transaction() as ops:
                uid = ops.insert(self.table, **{"name": "test3", "createtime": 3})
                ops.update(self.table, **{"name": "test2", "createtime": "test", "uid": uid})
        rows = sqlcnx.select(self.table, -1)
        # check that row has been inserted
        self.assertEqual(len(rows), 1)

# Load test suites
def _suites():
    return [
        MySQLContextTestSuite
    ]

# Load tests
def loadSuites():
    # global test suite for this module
    gsuite = unittest.TestSuite()
    for suite in _suites():
        gsuite.addTest(unittest.TestLoader().loadTestsFromTestCase(suite))
    return gsuite

if __name__ == '__main__':
    suite = loadSuites()
    print ""
    print "### Running tests ###"
    print "-" * 70
    unittest.TextTestRunner(verbosity=2).run(suite)
