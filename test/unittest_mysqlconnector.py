#!/usr/bin/env python

import unittest
import src.config as config
import src.connector.mysqlconnector as mysqlconnector
from src.connector.mysqlconnector import QuerySource, QueryValues, Query, MySqlConnector
from types import DictType, IntType, ListType
import uuid

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
        #return uuid.uuid4().hex
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
        self.connector.disconnect()

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

    def test_transactions(self):
        self.assertEqual(self.connector.cnx.in_transaction, False)
        # payload
        def payload(name, marked=1):
            payload = {
                "type": "insert",
                "schema": self.schema(),
                "table": self.table(),
                "body": { "name": name, "marked": marked },
                "predicate": {}
            }
            return payload
        print ""

        ###############################################
        # start transaction 1
        self.connector.begin_transaction()
        # insert couple of records
        self.connector.dml(payload("test-record-1", 0), atomic=False)
        self.connector.dml(payload("test-record-2", 1), atomic=False)
        # select those records
        result = self.connector.sql({
            "type": "select",
            "schema": self.schema(),
            "table": self.table(),
            "body": { "name": None, "marked": None },
            "predicate": {}
        }, atomic=False, fetchone=False)
        self.assertEqual(type(result), ListType)
        self.assertEqual(len(result), 2)
        marked_all = 0
        for obj in result:
            marked_all += obj[unicode("marked")]
        self.assertEqual(marked_all, 1)
        # update one record
        self.connector.dml({
            "type": "update",
            "schema": self.schema(),
            "table": self.table(),
            "body": { "marked": 1 },
            "predicate": { "marked": 0 }
        }, atomic=False)
        # close transaction 1
        self.connector.commit()
        # check transaction 1 state
        self.assertEqual(self.connector.cnx.in_transaction, False)
        # check those records
        result = self.connector.sql({
            "type": "select",
            "schema": self.schema(),
            "table": self.table(),
            "body": { "name": None, "marked": None },
            "predicate": { "marked": 1 }
        }, atomic=True, fetchone=False)
        self.assertEqual(type(result), ListType)
        self.assertEqual(len(result), 2)
        marked_all = 0
        for obj in result:
            marked_all += obj[unicode("marked")]
        self.assertEqual(marked_all, 2)
        print ":Transaction 1 [insert/update commit] - OK"

        ###############################################
        # start transaction 2
        self.connector.begin_transaction()
        # select records
        result = self.connector.sql({
            "type": "select",
            "schema": self.schema(),
            "table": self.table(),
            "body": { "name": None, "marked": None },
            "predicate": {}
        }, atomic=False, fetchone=False)
        self.assertEqual(type(result), ListType)
        self.assertEqual(len(result), 2)
        marked_all = 0
        for obj in result:
            marked_all += obj[unicode("marked")]
        self.assertEqual(marked_all, 2)
        # delete records
        self.connector.dml({
            "type": "delete",
            "schema": self.schema(),
            "table": self.table(),
            "body": {},
            "predicate": { "marked": 1 }
        }, atomic=False)
        # close transaction 2
        self.connector.commit()
        # check transaction 2 state
        self.assertEqual(self.connector.cnx.in_transaction, False)
        # check records
        result = self.connector.sql({
            "type": "select",
            "schema": self.schema(),
            "table": self.table(),
            "body": { "name": None, "marked": None },
            "predicate": {}
        }, atomic=True, fetchone=False)
        self.assertEqual(result, [])
        print ":Transaction 2 [delete commit] - OK"

        ###############################################
        # start transaction 3
        self.connector.begin_transaction()
        try:
            # insert couple of records
            self.connector.dml(payload("test-record-3", 0), atomic=False)
            self.connector.dml(payload("test-record-4", 1), atomic=False)
            # update records
            self.connector.dml({
                "type": "update",
                "schema": self.schema(),
                "table": self.table(),
                "body": { "marked": 1 },
                "predicate": { "marked": 0 }
            }, atomic=False)
            # raise error
            raise KeyError("Test error")
        # close transaction 3
        except KeyError as e:
            self.connector.rollback()
        else:
            self.connector.commit()
        # check transaction 3 state
        self.assertEqual(self.connector.cnx.in_transaction, False)
        # check that there is no records in table
        result = self.connector.sql({
            "type": "select",
            "schema": self.schema(),
            "table": self.table(),
            "body": { "name": None, "marked": None },
            "predicate": {}
        }, atomic=True, fetchone=False)
        self.assertEqual(result, [])
        print ":Transaction 3 [insert/update rollback] - OK"

    def test_select_fetch(self):
        # insert couple of records
        self.connector.dml({
            "type": "insert",
            "schema": self.schema(),
            "table": self.table(),
            "body": { "name": "test-record-10", "marked": 0 },
            "predicate": {}
        })
        self.connector.dml({
            "type": "insert",
            "schema": self.schema(),
            "table": self.table(),
            "body": { "name": "test-record-11", "marked": 1 },
            "predicate": {}
        })
        print ""
        # fetch one record
        result = self.connector.sql({
            "type": "select",
            "schema": self.schema(),
            "table": self.table(),
            "body": { "name": None, "marked": None },
            "predicate": {}
        })
        self.assertEqual(type(result), DictType)
        for key in result.keys():
            self.assertNotEqual(result[key], None)
        print ":Select one record - OK"
        # fetch all records
        result = self.connector.sql({
            "type": "select",
            "schema": self.schema(),
            "table": self.table(),
            "body": { "name": None, "marked": None },
            "predicate": {}
        }, fetchone=False)
        self.assertEqual(type(result), ListType)
        for obj in result:
            for key in obj:
                self.assertNotEqual(obj[key], None)
        print ":Select many records - OK"
        # fetch empty result
        result = self.connector.sql({
            "type": "select",
            "schema": self.schema(),
            "table": self.table(),
            "body": { "name": None, "marked": None },
            "predicate": {"id": None}
        })
        self.assertEqual(result, None)
        print ":Select empty record - OK"
        # fetch empty results list
        result = self.connector.sql({
            "type": "select",
            "schema": self.schema(),
            "table": self.table(),
            "body": { "name": None, "marked": None },
            "predicate": {"id": None}
        }, fetchone=False)
        self.assertEqual(result, [])
        print ":Select empty records list - OK"
        self.assertEqual(self.connector.cnx.in_transaction, False)

    def test_select_orderby(self):
        def insertdata(name, marked):
            return {
                "type": "insert",
                "schema": self.schema(),
                "table": self.table(),
                "body": { "name": name, "marked": marked },
                "predicate": {}
            }
        data = [
            {"name": "select-order-1", "marked": 1},
            {"name": "select-order-2", "marked": 1},
            {"name": "select-order-1", "marked": 0},
            {"name": "select-order-5", "marked": 1},
            {"name": "select-order-5", "marked": 0},
            {"name": "select-order-2", "marked": 0}
        ]
        for obj in data:
            self.connector.dml(insertdata(obj["name"], obj["marked"]))
        print ""
        # select unsorted
        result = self.connector.sql({
            "type": "select",
            "schema": self.schema(),
            "table": self.table(),
            "body": { "name": None, "marked": None },
            "predicate": {}
        }, fetchone=False)
        # check result with data
        for i in range(len(data)):
            self.assertEqual(data[i]["name"], result[i][unicode("name")])
            self.assertEqual(data[i]["marked"], result[i][unicode("marked")])
        print ":OrderBy [unsorted] - OK"
        # select all records sorted by marked
        result = self.connector.sql({
            "type": "select",
            "schema": self.schema(),
            "table": self.table(),
            "body": { "name": None, "marked": None },
            "predicate": {},
            "orderby": {
                "marked": Query.ORDER_BY_ASC
            }
        }, fetchone=False)
        sorted_by_marked = sorted([x.values() for x in data], key=lambda t:t[1])
        result_list = [x.values() for x in result]
        self.assertEqual(sorted_by_marked, result_list)
        print ":OrderBy [sorted by marked asc] - OK"
        # select all records sorted by name
        result = self.connector.sql({
            "type": "select",
            "schema": self.schema(),
            "table": self.table(),
            "body": { "name": None, "marked": None },
            "predicate": {},
            "orderby": {
                "name": Query.ORDER_BY_DESC
            }
        }, fetchone=False)
        sorted_by_name = sorted([x.values() for x in data], key=lambda t:t[0], reverse=True)
        result_list = [x.values() for x in result]
        self.assertEqual(sorted_by_name, result_list)
        print ":OrderBy [sorted by name desc] - OK"
        # select all records sorted by name and marked
        result = self.connector.sql({
            "type": "select",
            "schema": self.schema(),
            "table": self.table(),
            "body": { "name": None, "marked": None },
            "predicate": {},
            "orderby": {
                "name": Query.ORDER_BY_ASC,
                "marked": Query.ORDER_BY_ASC
            }
        }, fetchone=False)
        sorted_by_all = sorted([x.values() for x in data])
        result_list = [x.values() for x in result]
        self.assertEqual(sorted_by_all, result_list)
        print ":OrderBy [sorted by name asc, marked asc] - OK"


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
