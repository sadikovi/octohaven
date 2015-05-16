import src.config as config
import mysql.connector
from mysql.connector import errorcode
import uuid
from types import DictType

# create connection
cnx = mysql.connector.connect(user=config.mysql_user, password=config.mysql_pass, host=config.mysql_host, database=config.db_schema)

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

class QuerySource(object):
    def __init__(self, schema, table):
        self.schema = "%s" %(schema)
        self.table = "%s" %(table)
    def source(self):
        return "%s.%s" %(self.schema, self.table)

class QueryValues(object):
    def __init__(self, dict):
        self.metavalues = []
        self.mapvalues = []
        if type(dict) is not DictType:
            raise StandardError("Not a dict")
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
        if self.type == "select":
            bdy = ["%s"%(key) for t in self.body.metavalues for key, value in t.items()]
            src = self.source.source()
            prd = [("%s"%(key) + "=%" + "(%s)"%(value) + "s") for t in self.data.metavalues for key, value in t.items()]
            query = "select %s from %s where (%s)" %(", ".join(bdy), src, " and ".join(prd))
            return query
        elif self.type == "insert":
            src = self.source.source()
            cols = ["%s"%(key) for t in self.data.metavalues for key, value in t.items()]
            vals = [("%" + "(%s)"%(value) + "s") for t in self.data.metavalues for key, value in t.items()]
            query = "insert into %s (%s) values (%s)" %(src, ", ".join(cols), ", ".join(vals))
            return query
        elif self.type == "delete":
            src = self.source.source()
            prd = [("%s"%(key) + "=%" + "(%s)"%(value) + "s") for t in self.data.metavalues for key, value in t.items()]
            query = "delete from %s where (%s)" %(src, " and ".join(prd))
            return query
        elif self.type == "update":
            bdy = [("%s"%(key) + "=%" + "(%s)"%(value) + "s") for t in self.body.metavalues for key, value in t.items()]
            src = self.source.source()
            prd = [("%s"%(key) + "=%" + "(%s)"%(value) + "s") for t in self.data.metavalues for key, value in t.items()]
            query = "update %s set %s where (%s)" %(src, ", ".join(bdy), " and ".join(prd))
            return query
        else:
            return None
    def mapdict(self):
        mapvalues = {}
        # insert body
        pairs = self.body.mapvalues + self.data.mapvalues
        for t in pairs:
            for key, value in t.items():
                mapvalues[key] = value
        return mapvalues

def processPayload(payload):
    query = Query(payload["type"], payload["schema"], payload["table"], payload["body"], payload["predicate"])
    return query

# internal insert
def _executeStatement(operation, cursor, payload):
    res = processPayload(payload)
    if operation == "sql" and res.type == "select":
        """sql - select"""
    elif operation == "dml" and res.type in ["insert", "delete", "update"]:
        """dml operation is found"""
    else:
        raise StandardError("Wrong use of %s command, use matched method for SQL/DML operation" %(res.type))
    # operation matches type - execute query
    cursor.execute(res.metaquery(), res.mapdict())

def dml(payload, commit=True, lastrowid=False):
    # otherwise open connection
    if not cnx.is_connected():
        cnx.connect()
    # get cursor
    result = False
    try:
        cursor = cnx.cursor()
        # run command
        _executeStatement("dml", cursor, payload)
        # get last row id, if feature is on
        result = cursor.lastrowid if lastrowid else True
        # commit
        if commit:
            cnx.commit()
    except BaseException as e:
        # TODO: log error
        if commit: cnx.rollback()
        print e
    finally:
        cursor.close()
    # return result
    return result

def sql(payload, fetchone=True, atomic=True):
    # otherwise open connection
    if not cnx.is_connected():
        cnx.connect()
    result = None
    cursor = cnx.cursor(dictionary=True, buffered=True)
    try:
        _executeStatement("sql", cursor, payload)
        if fetchone:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
    except BaseException as e:
        # TODO: log error
        # raise e
        print e
    finally:
        if cnx.in_transaction and atomic:
            cnx.rollback()
        cursor.close()
    # return result
    return result
