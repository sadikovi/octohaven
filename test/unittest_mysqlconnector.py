#!/usr/bin/env python

import unittest
import src.config as config
import src.connector.mysqlconnector as mysqlconnector
from src.connector.mysqlconnector import QuerySource, QueryValues, Query, MySqlConnector
from types import DictType, IntType

class QuerySource_TS(unittest.TestCase):
    def test_querysource(self):
        source = [("schema", "table"), ("s.s", "t.t", " ", " ")]
        for t in source:
            schema, table = t[0], t[1]
            if schema.strip() and table.strip():
                qsource = QuerySource(schema, table)
                # length of schema/table list is always 2
                self.assertEqual(len(qsource.source().split(".")), 2)
            else:
                with self.assertRaises(StandardError):
                    qsource = QuerySource(schema, table)

class QueryValues_TS(unittest.TestCase):
    def test_init(self):
        source = [None, {}, {"key2": "1", "key2": 1, "key3": "value3"}]
        for t in source:
            if type(t) is DictType:
                qvalues = QueryValues(t)
                if t:
                    # assemble source back
                    res = {}
                    for i, dict in enumerate(qvalues.metavalues):
                        for key, value in dict.items():
                            res[key] = qvalues.mapvalues[i][value]
                    self.assertEqual(res, t)
                else:
                    self.assertEqual(qvalues.metavalues, [])
                    self.assertEqual(qvalues.mapvalues, [])
            else:
                with self.assertRaises(StandardError):
                    qvalues = QueryValues(t)

class Query_TS(unittest.TestCase):
    pass

class MySqlConnector_UT(unittest.TestCase):
    def schema(self):
        return config.db_schema

    def table(self):
        return "test_connector"

    def ddl_create(self):
        table = """
            create table %s.%s (
                id int(8) unsigned auto_increment primary key,
                name varchar(255),
                marked tinyint(1) unsigned
            ) engine=InnoDB;
        """ %(self.schema(), self.table())
        return table

    def ddl_drop(self):
        table = """
            drop table %s.%s;
        """ %(self.schema(), self.table())
        return table

    def setUp(self):
        # create test table
        settings = {
            "user": config.mysql_user,
            "pass": config.mysql_pass,
            "host": config.mysql_host,
            "schema": config.db_schema
        }
        self.connector = MySqlConnector(settings)
        cursor = self.connector.cnx.cursor()
        cursor.execute(self.ddl_create())
        if self.connector.cnx.in_transaction:
            print "SetUp: Connector is in transaction state"
            connector.cnx.rollback()
        cursor.close()

    def tearDown(self):
        # drop test table
        cursor = self.connector.cnx.cursor()
        cursor.execute(self.ddl_drop())
        if self.connector.cnx.in_transaction:
            print "TearDown: Connector is in transaction state"
            connector.cnx.rollback()
        cursor.close()
        self.connector.cnx.close()
        self.connector = None

    def test_mysqlconnector(self):
        print ""
        # insert record
        payload = {
            "type": "insert",
            "schema": self.schema(),
            "table": self.table(),
            "body": {
                "name": "test-record",
                "marked": 1
            },
            "predicate": {}
        }
        result = self.connector.dml(payload, lastrowid=True)
        # check that we get back row id
        self.assertEqual(type(result), IntType)
        print ":Inserting test record - OK"
        # fetch obj back
        payload = {
            "type": "select",
            "schema": self.schema(),
            "table": self.table(),
            "body": {
                "id": None,
                "name": None,
                "marked": None
            },
            "predicate": { "id": result }
        }
        obj = self.connector.sql(payload)
        self.assertEqual(obj["id"], result)
        self.assertEqual(obj["name"], "test-record")
        self.assertEqual(obj["marked"], 1)
        print ":Checking test record after insert - OK"
        # update marked
        payload = {
            "type": "update",
            "schema": self.schema(),
            "table": self.table(),
            "body": {
                "marked": 0
            },
            "predicate": { "id": obj["id"] }
        }
        result = self.connector.dml(payload)
        self.assertEqual(result, True)
        print ":Updating test record - OK"
        # fetch object back
        payload = {
            "type": "select",
            "schema": self.schema(),
            "table": self.table(),
            "body": {
                "id": None,
                "name": None,
                "marked": None
            },
            "predicate": { "id": obj["id"] }
        }
        obj = self.connector.sql(payload)
        self.assertEqual(obj["id"], result)
        self.assertEqual(obj["name"], "test-record")
        self.assertEqual(obj["marked"], 0)
        print ":Checking test record after update - OK"
        # delete record
        payload = {
            "type": "delete",
            "schema": self.schema(),
            "table": self.table(),
            "body": {},
            "predicate": { "id": obj["id"] }
        }
        result = self.connector.dml(payload)
        self.assertEqual(result, True)
        print ":Deleting test record - OK"
        # fetch object back, this time it has to be None
        payload = {
            "type": "select",
            "schema": self.schema(),
            "table": self.table(),
            "body": {
                "id": None,
                "name": None,
                "marked": None
            },
            "predicate": { "id": obj["id"] }
        }
        obj = self.connector.sql(payload)
        self.assertEqual(obj, None)
        print ":Checking test record after delete - OK"

    def test_failures(self):
        print ""
        # running dml operation as sql
        payload = {
            "type": "insert",
            "schema": self.schema(),
            "table": self.table(),
            "body": {
                "name": "test-record",
                "marked": 1
            },
            "predicate": {}
        }
        with self.assertRaises(StandardError):
            self.connector.sql(payload)
        print ":Failure to run Insert as SQL operation - OK"
        # running sql operation as dml
        payload = {
            "type": "select",
            "schema": self.schema(),
            "table": self.table(),
            "body": {
                "name": None,
                "marked": None
            },
            "predicate": {
                "id": 1
            }
        }
        with self.assertRaises(StandardError):
            self.connector.dml(payload)
        print ":Failure to run Select as DML operation - OK"
        # running empty dict for sql
        with self.assertRaises(KeyError):
            self.connector.sql({})
        print ":Failure to use empty payload for SQL - OK"
        # running empty dict for dml
        with self.assertRaises(KeyError):
            self.connector.dml({})
        print ":Failure to use empty payload for DML- OK"
        # running empty body and predicate
        payload = {
            "type": "select",
            "schema": self.schema(),
            "table": self.table(),
            "body": None,
            "predicate": None
        }
        with self.assertRaises(StandardError):
            self.connector.dml(payload)
        print ":Failure to use payload without body and predicate - OK"

# Load test suites
def _suites():
    return [
        QuerySource_TS,
        QueryValues_TS,
        Query_TS,
        MySqlConnector_UT
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
