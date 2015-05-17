#!/usr/bin/env python

import src.config as config
import mysql.connector
from mysql.connector import errorcode
import uuid
from types import DictType

# design payload template
"""
template = {
    "type": "select | delete | update | insert"
    "schema": "",
    "table": "",
    "body": {
        "key": "value",
        "key": "value"
    },
    "predicate": {
        "key": "value",
        "key": "value"
    }
}
"""
# dml operations
DML = "dml"
DML_INSERT = "insert"
DML_UPDATE = "update"
DML_DELETE = "delete"
# sql operations
SQL = "sql"
SQL_SELECT = "select"

class QuerySource(object):
    def __init__(self, schema, table):
        schema = schema.replace(".", "_").strip()
        table = table.replace(".", "_").strip()
        if not schema or not table:
            raise StandardError("Wrong schema or table name provided")
        self.schema = "%s" %(schema)
        self.table = "%s" %(table)
    def source(self):
        return "%s.%s" %(self.schema, self.table)

class QueryValues(object):
    def __init__(self, dict):
        self.metavalues = []
        self.mapvalues = []
        if type(dict) is not DictType:
            raise StandardError("Values object is not a DictType")
        for key, value in dict.items():
            # init key and pairs
            generatedkey = uuid.uuid4().hex
            metapair, mappair = {}, {}
            # add keys to pairs
            metapair[key] = generatedkey
            mappair[generatedkey] = value
            # inset values
            self.metavalues.append(metapair)
            self.mapvalues.append(mappair)

class Query(object):
    def __init__(self, type, schema, table, body, predicate):
        self.type = ("%s"%(type)).lower()
        self.source = QuerySource(schema, table)
        self.body = QueryValues(body)
        self.data = QueryValues(predicate)
    def metaquery(self):
        if self.type == SQL_SELECT:
            # prepare values
            bdy = ["%s"%(key) for t in self.body.metavalues for key, value in t.items()]
            prd = [("%s"%(key) + " = %" + "(%s)"%(value) + "s") for t in self.data.metavalues for key, value in t.items()]
            # prepare query
            querybody = ", ".join(bdy) if len(bdy) else "*"
            querysource = self.source.source()
            querypredicate = " and ".join(prd) if len(prd) else "1 = 1"
            query = "select %s from %s where (%s)" %(querybody, querysource, querypredicate)
            return query
        elif self.type == DML_INSERT:
            src = self.source.source()
            cols = ["%s"%(key) for t in self.body.metavalues for key, value in t.items()]
            vals = [("%" + "(%s)"%(value) + "s") for t in self.body.metavalues for key, value in t.items()]
            query = "insert into %s (%s) values (%s)" %(src, ", ".join(cols), ", ".join(vals))
            return query
        elif self.type == DML_DELETE:
            prd = [("%s"%(key) + " = %" + "(%s)"%(value) + "s") for t in self.data.metavalues for key, value in t.items()]
            # prepare query
            querysource = self.source.source()
            querypredicate = " and ".join(prd) if len(prd) else "1 = 1"
            query = "delete from %s where (%s)" %(querysource, querypredicate)
            return query
        elif self.type == DML_UPDATE:
            bdy = [("%s"%(key) + " = %" + "(%s)"%(value) + "s") for t in self.body.metavalues for key, value in t.items()]
            prd = [("%s"%(key) + " = %" + "(%s)"%(value) + "s") for t in self.data.metavalues for key, value in t.items()]
            # prepare query
            querybody = ", ".join(bdy)
            querysource = self.source.source()
            querypredicate = " and ".join(prd) if len(prd) else "1 = 1"
            query = "update %s set %s where (%s)" %(querysource, querybody, querypredicate)
            return query
        else:
            return None
    def mapdict(self):
        mapvalues = {}
        # insert body
        pairs = self.body.mapvalues + self.data.mapvalues
        for t in pairs:
            # must be only one pair in t
            for key, value in t.items():
                mapvalues[key] = value
        return mapvalues

class MySqlConnector(object):
    def __init__(self, settings):
        if not settings or type(settings) is not DictType:
            raise StandardError("Settings are undefined")
        # connect to the server
        self.cnx = mysql.connector.connect(
            user=settings["user"],
            password=settings["pass"],
            host=settings["host"],
            database=settings["schema"]
        )

    # process payload and return query
    def _processPayload(self, payload):
        return Query(
            payload["type"],
            payload["schema"],
            payload["table"],
            payload["body"],
            payload["predicate"]
        )

    # execute statement
    def _executeStatement(self, operation, cursor, payload):
        res = self._processPayload(payload)
        if not res:
            raise StandardError("Object is not Query type")
        # check if operation is SQL or DML
        opmatch = False or (operation == SQL and res.type == SQL_SELECT)
        opmatch = opmatch or (operation == DML and res.type in [DML_INSERT, DML_DELETE, DML_UPDATE])
        if opmatch:
            # operation matches type - execute query
            cursor.execute(res.metaquery(), res.mapdict())
        else:
            raise StandardError("Wrong use of %s command, use method for SQL/DML operation" %(res.type))

    # call dml operation
    def dml(self, payload, commit=True, lastrowid=False):
        if not self.cnx.is_connected():
            self.cnx.connect()
        result = False
        try:
            cursor = self.cnx.cursor()
            # run command
            self._executeStatement(DML, cursor, payload)
            # get last row id, if feature is on
            result = cursor.lastrowid if lastrowid else True
            # commit
            if commit:
                self.cnx.commit()
        except BaseException as e:
            # TODO: log error
            if commit: self.cnx.rollback()
            raise e
        finally:
            cursor.close()
        # return result
        return result

    # execute sql operation
    def sql(self, payload, fetchone=True, atomic=True):
        if not self.cnx.is_connected():
            self.cnx.connect()
        result = None
        cursor = self.cnx.cursor(dictionary=True, buffered=True)
        try:
            self._executeStatement(SQL, cursor, payload)
            if fetchone:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
        except BaseException as e:
            # TODO: log error
            raise e
        finally:
            if self.cnx.in_transaction and atomic:
                self.cnx.rollback()
            cursor.close()
        # return result
        return result
