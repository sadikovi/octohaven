#!/usr/bin/env python

import utils
from types import DictType
from src.octo.mysqlcontext import MySQLContext

# Storage manager is data provider to MySQLContext. It manages all the queries in the
# application.
class StorageManager(object):
    def __init__(self, sqlContext):
        utils.assertInstance(sqlContext, MySQLContext)
        self.sqlContext = sqlContext

    ############################################################
    # Template API
    ############################################################
    # Insert data [name: String, createtime: Long, content: String] into table and return
    # new id for that template
    def createTemplate(self, name, createtime, content):
        rowid = None
        with self.sqlContext.cursor(with_transaction=True) as cr:
            dml = ("INSERT INTO templates(name, createtime, content) "
                    "VALUES(%(name)s, %(createtime)s, %(content)s)")
            cr.execute(dml, {"name": name, "createtime": createtime, "content": content})
            rowid = cr.lastrowid
        return rowid

    # Fetch all available templates [uid, name, createtime, content] and sort them by name.
    # Return results as list of dict objects with fields similar to schema.
    def getTemplates(self):
        data = None
        with self.sqlContext.cursor(with_transaction=False) as cr:
            sql = "SELECT uid, name, createtime, content FROM templates ORDER BY name ASC"
            cr.execute(sql)
            data = cr.fetchall()
        return data

    # Fetch one record [uid, name, createtime, content] based on uid provided. Return dict object
    # with fields given as column names.
    def getTemplate(self, uid):
        data = None
        with self.sqlContext.cursor(with_transaction=False) as cr:
            sql = "SELECT uid, name, createtime, content FROM templates WHERE uid = %(uid)s"
            cr.execute(sql, {"uid": uid})
            data = cr.fetchone()
        return data

    # Delete record based on uid specified
    def deleteTemplate(self, uid):
        with self.sqlContext.cursor(with_transaction=True) as cr:
            dml = "DELETE FROM templates WHERE uid = %(uid)s"
            cr.execute(dml, {"uid": uid})
