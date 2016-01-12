#!/usr/bin/env python

import unittest, test, mysql, src.octo.utils as utils
from src.octo.mysqlcontext import MySQLContext, MySQLLock
from mysql.connector.errors import PoolError, Error as SQLGlobalError

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
        MySQLLock.reset()

    def tearDown(self):
        pass

    def test_init1(self):
        sqlcnx = MySQLContext(**self.config)
        self.assertEqual(len(sqlcnx.cnxpool.pool_name), 32)
        self.assertEqual(sqlcnx.cnxpool.pool_size, 2)

    # init specific name and pool size
    def test_init2(self):
        self.config["pool_name"] = "dummy"
        self.config["pool_size"] = 10
        sqlcnx = MySQLContext(**self.config)
        self.assertEqual(sqlcnx.cnxpool.pool_name, self.config["pool_name"])
        self.assertEqual(sqlcnx.cnxpool.pool_size, self.config["pool_size"])

    # test allowed number of connections per application
    def test_lockNumContext(self):
        sqlcnx1 = MySQLContext(**self.config)
        with self.assertRaises(StandardError):
            sqlcnx2 = MySQLContext(**self.config)

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

    def test_create(self):
        sqlcnx = MySQLContext(**self.config)
        sqlcnx.dropTable(self.table)
        status = sqlcnx.createTable(self.ddl)
        self.assertEqual(status, True)
        # try creating table again
        status = sqlcnx.createTable(self.ddl)
        self.assertEqual(status, False)

    def test_drop(self):
        sqlcnx = MySQLContext(**self.config)
        sqlcnx.createTable(self.ddl)
        status = sqlcnx.dropTable(self.table)
        self.assertEqual(status, True)
        # try deleting it again
        status = sqlcnx.dropTable(self.table)
        self.assertEqual(status, False)

    def test_insert(self):
        sqlcnx = MySQLContext(**self.config)
        sqlcnx.dropTable(self.table)
        sqlcnx.createTable(self.ddl)
        uid = None
        with sqlcnx.cursor(with_transaction=True) as cr:
            dml = "INSERT INTO test (name, createtime) VALUES(%(name)s, %(createtime)s)"
            cr.execute(dml, {"name": "a", "createtime": 123})
            uid = cr.lastrowid
        # fetching without transaction
        rows = None
        with sqlcnx.cursor(with_transaction=False) as cr:
            sql = "SELECT uid, name, createtime FROM test WHERE uid = %(uid)s"
            cr.execute(sql, {"uid": uid})
            rows = cr.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["uid"], uid)
        self.assertEqual(rows[0]["name"], "a")
        self.assertEqual(rows[0]["createtime"], 123)
        # test failed transaction
        with self.assertRaises(StandardError):
            with sqlcnx.cursor(with_transaction=True) as cr:
                dml = "INSERT INTO test (name, createtime) VALUES(%(name)s, %(createtime)s)"
                cr.execute(dml, {"name": "a", "createtime": 123})
                raise StandardError()
        # check that no records were inserted
        with sqlcnx.cursor(with_transaction=False) as cr:
            sql = "SELECT uid, name, createtime FROM test"
            cr.execute(sql)
            rows = cr.fetchall()
        self.assertEqual(len(rows), 1)

    def test_transaction(self):
        sqlcnx = MySQLContext(**self.config)
        sqlcnx.dropTable(self.table)
        sqlcnx.createTable(self.ddl)
        uid = None
        with sqlcnx.cursor(with_transaction=True) as cr:
            dml = "INSERT INTO test (name, createtime) VALUES(%(name)s, %(time)s)"
            cr.execute(dml, {"name": "test1", "time": 1})
            uid = cr.lastrowid
            # now update that record
            dml = "UPDATE test SET name = %(name)s, createtime = %(time)s WHERE uid = %(uid)s"
            cr.execute(dml, {"name": "test2", "time": 2, "uid": uid})
        # fetch updated record
        with sqlcnx.cursor(with_transaction=False) as cr:
            sql = "SELECT uid, name, createtime FROM test"
            cr.execute(sql)
            rows = cr.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["uid"], uid)
        self.assertEqual(rows[0]["name"], "test2")
        self.assertEqual(rows[0]["createtime"], 2)
        # test failure, should rollback inserted records
        with self.assertRaises(SQLGlobalError):
            with sqlcnx.cursor(with_transaction=True) as cr:
                dml = "INSERT INTO test (name, createtime) VALUES(%(name)s, %(time)s)"
                cr.execute(dml, {"name": "test1", "time": 1})
                uid = cr.lastrowid
                dml = "UPDATE test SET name = %(n)s, createtime = %(t)s WHERE uid = %(uid)s"
                cr.execute(dml, {"n": "test2", "t": "test", "uid": uid})
        # fetch records
        with sqlcnx.cursor(with_transaction=False) as cr:
            sql = "SELECT uid, name, createtime FROM test"
            cr.execute(sql)
            rows = cr.fetchall()
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
