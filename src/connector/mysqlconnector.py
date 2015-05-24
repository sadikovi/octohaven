#!/usr/bin/env python

import src.mysql.config as config
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
    },
    "orderby": {
        "key": "value",
        "key": "value"
    }
}
"""

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
    # dml operations
    DML = "dml"
    DML_INSERT = "insert"
    DML_UPDATE = "update"
    DML_DELETE = "delete"
    # sql operations
    SQL = "sql"
    SQL_SELECT = "select"
    # order by (default is asc)
    ORDER_BY_ASC = "ASC"
    ORDER_BY_DESC = "DESC"

    def __init__(self, querytype, schema, table, body, predicate, orderby=None):
        self.type = ("%s"%(querytype)).lower()
        self.source = QuerySource(schema, table)
        self.body = QueryValues(body)
        self.data = QueryValues(predicate)
        self.orderby = orderby if type(orderby) is DictType else None
    def metaquery(self):
        if self.type == Query.SQL_SELECT:
            # prepare values
            bdy = ["%s"%(key) for t in self.body.metavalues for key, value in t.items()]
            prd = [("%s"%(key) + " = %" + "(%s)"%(value) + "s") for t in self.data.metavalues for key, value in t.items()]
            # prepare query
            querybody = ", ".join(bdy) if len(bdy) else "*"
            querysource = self.source.source()
            querypredicate = " and ".join(prd) if len(prd) else "1 = 1"
            query = "select %s from %s where (%s)" %(querybody, querysource, querypredicate)
            if self.orderby:
                obparts = ["%s %s"%(key, value) for key, value in self.orderby.items()]
                queryorderby = "order by %s"%(", ".join(obparts))
                query += " %s"%(queryorderby)
            return query
        elif self.type == Query.DML_INSERT:
            src = self.source.source()
            cols = ["%s"%(key) for t in self.body.metavalues for key, value in t.items()]
            vals = [("%" + "(%s)"%(value) + "s") for t in self.body.metavalues for key, value in t.items()]
            query = "insert into %s (%s) values (%s)" %(src, ", ".join(cols), ", ".join(vals))
            return query
        elif self.type == Query.DML_DELETE:
            prd = [("%s"%(key) + " = %" + "(%s)"%(value) + "s") for t in self.data.metavalues for key, value in t.items()]
            # prepare query
            querysource = self.source.source()
            querypredicate = " and ".join(prd) if len(prd) else "1 = 1"
            query = "delete from %s where (%s)" %(querysource, querypredicate)
            return query
        elif self.type == Query.DML_UPDATE:
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
        self.settings = settings
        # connector
        self.cnx = None
        # connect to the server
        self.reconnect()

    # connection and reconnection to the server
    def reconnect(self, settings=None, forced=False):
        settings = settings or self.settings
        # not sure about this, maybe we should disconnect
        if self.cnx and self.cnx.is_connected() and forced:
            self.disconnect()
        # connection
        if not self.cnx:
            self.cnx = mysql.connector.connect(
                user=settings["user"],
                password=settings["pass"],
                host=settings["host"],
                database=settings["schema"]
            )
        # if it is not connected - reconnect
        if not self.cnx.is_connected():
            self.cnx.connect()

    # disconnect
    def disconnect(self):
        if self.cnx:
            self.cnx.disconnect()
            self.cnx = None

    # checks if connector is in transaction state and rollbacks in atomic mode
    def isatomic(self, atomic):
        if atomic and self.cnx.in_transaction:
            # discard previous transaction
            self.cnx.rollback()

    def commit(self):
        self.cnx.commit()

    def rollback(self):
        self.cnx.rollback()

    # process payload and return query
    def _processPayload(self, payload):
        _orderby = payload["orderby"] if "orderby" in payload else None
        return Query(
            payload["type"],
            payload["schema"],
            payload["table"],
            payload["body"],
            payload["predicate"],
            _orderby
        )

    # execute statement
    def _executeStatement(self, operation, cursor, payload):
        res = self._processPayload(payload)
        if not res:
            raise StandardError("Object is not Query type")
        # check if operation is SQL or DML
        opmatch = False or (operation == Query.SQL and res.type == Query.SQL_SELECT)
        opmatch = opmatch or (operation == Query.DML and res.type in
            [Query.DML_INSERT, Query.DML_DELETE, Query.DML_UPDATE])
        if opmatch:
            # operation matches type - execute query
            cursor.execute(res.metaquery(), res.mapdict())
        else:
            raise StandardError("Wrong use of %s command, use method for SQL/DML operation" %(res.type))

    # call dml operation
    def dml(self, payload, atomic=True, lastrowid=False):
        self.reconnect()
        # if operation is atomic it is performed in its own transaction.
        self.isatomic(atomic)
        result = False
        try:
            cursor = self.cnx.cursor()
            # run command
            self._executeStatement(Query.DML, cursor, payload)
            # get last row id, if feature is on
            result = cursor.lastrowid if lastrowid else True
            # commit
            if atomic:
                self.cnx.commit()
        except BaseException as e:
            # TODO: log error
            if atomic:
                self.cnx.rollback()
            raise e
        finally:
            cursor.close()
        # return result
        return result

    # execute sql operation
    def sql(self, payload, fetchone=True, atomic=True):
        self.reconnect()
        # if operation is atomic it is performed in its own transaction.
        self.isatomic(atomic)
        # execute statement
        result = None
        cursor = self.cnx.cursor(dictionary=True, buffered=True)
        try:
            self._executeStatement(Query.SQL, cursor, payload)
            if fetchone:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
        except BaseException as e:
            # TODO: log error
            raise e
        finally:
            self.isatomic(atomic)
            cursor.close()
        # return result
        return result

    # call begin transaction
    def begin_transaction(self, ignoreprevious=False, consistent_snapshot=True, isolation_level="SERIALIZABLE"):
        self.reconnect()
        # check if cnx is already in transaction state
        # if True we rollback any previous transactions
        if self.cnx.in_transaction:
            if ignoreprevious:
                self.cnx.rollback()
            else:
                raise StandardError("Transaction is in progress")
        # open transaction
        self.cnx.start_transaction(consistent_snapshot, isolation_level, readonly=False)
