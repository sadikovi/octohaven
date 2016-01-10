#!/usr/bin/env python

from octolog import Octolog

# `MySQLAtomicOperations` provides API to execute query or perform DML operations. It uses SQL
# blocks to build the command in a safe way avoiding injection whenever possible.
class MySQLAtomicOperations(Octolog, object):
    def __init__(self, cursor):
        # sql cursor to perform dml/sql operations, can be used directly to build special queries,
        # but it is recommended to use default methods
        self.cursor = cursor

    # Perform insertion into "table" with args as list of "column" - "value"
    def insert(self, table, **args):
        insert into test(name, time) values ("a", 1)
        insert into %(1)s (%(2)s, %(3)s) values (%(4)s, %(5)s)
        cols = args.keys()
        valcols = ["%s" for col in cols]
        dml = "INSERT INTO %s (%s) VALUES(%s) " % (table, ", ".join(cols), ", ".join(valcols))
        self.cursor.execute(dml, args)
        return self.cursor.lastrowid

    # Update columns for UID field
    def update(self, table, **args):
        if "uid" not in args:
            raise StandardError("Key 'uid' is not arguments %s" % args)
        cols = [key + " = " + "%(" + key + ")s" for key in args.keys() if key != "uid"]
        dml = "UPDATE %s SET %s WHERE uid = %ss" % (table, ", ".join(cols), "%(uid)")
        self.cursor.execute(dml, args)

    # Delete records for all the fields provided
    def delete(self, table, **args):
        cols = [key + " = " + "%(" + key + ")s" for key in args.keys()]
        dml = "DELETE FROM %s WHERE %s" % (table, " AND ".join(cols))
        self.cursor.execute(dml, args)

    # select table using limit, dictionary of sorting columns, e.g. {"name": "desc"}, and predicate
    # list "args"
    def select(self, table, limit, sort=None, args=None):
        limitClause = ""
        whereClause = ""
        orderClause = ""
        if limit > 0:
            limitClause = "LIMIT %s" % limit
        if sort:
            sortCols = ["%s %s" % (key, value) for key, value in args.items()]
            orderClause = "ORDER BY %s" % ", ".join(sortCols)
        if args:
            cols = [key + " = " + "%(" + key + ")s" for key in args.keys()]
            whereClause = "WHERE %s" % " AND ".join(cols)
        sql = "SELECT * FROM %s %s %s %s" % (table, whereClause, orderClause, limitClause)
        self.cursor.execute(sql, args)
        if limit > 0:
            return self.cursor.fetchmany(limit)
        else:
            return self.cursor.fetchall()
