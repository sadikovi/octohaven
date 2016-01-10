#!/usr/bin/env python

import re, uuid, utils
from types import IntType
from octolog import Octolog

# SQL DSL to build sql and dml queries with built-in validation of values, table names, and columns
# Default class to include logging and some other general things
class QueryBasic(Octolog, object):
    pass

class QueryType(QueryBasic):
    pass

# Validate table, column names, and other SQL special keywords
class QueryValidate(QueryBasic):
    @classmethod
    def _validate(cls, cmd, value):
        updatedValue = value.strip()
        groups = re.match(cmd, updatedValue)
        if groups is None:
            raise StandardError("Failed validation [%s]: %s" % (cmd, updatedValue))
        return groups.group(0)

    @classmethod
    def strict(cls, value):
        return cls._validate(r"^\w+$", value)

    @classmethod
    def soft(cls, value):
        return cls._validate(r"^[ \w\(\)]+$", value)

class SQLTable(QueryBasic):
    def __init__(self, name):
        self.name = QueryValidate.strict(str(name).lower())
        self.uid = "%s_%s" % (uuid.uuid4().hex, self.name)

    def join(jointype, col1, col2):
        return Join().join(jointype, col1, col2)

class SQLColumn(QueryBasic):
    def __init__(self, name, table):
        utils.assertInstance(table, SQLTable)
        self.table = table
        self.name = QueryValidate.strict(str(name).lower())
        self.uid = "%s_%s" % (self.table.uid, self.name)

    def asc(self):
        return SQLOrder(self, "asc")

    def desc(self):
        return SQLOrder(self, "desc")

class Join(QueryBasic):
    def __init__(self):
        self.conditions = []

    def join(self, jointype, col1, col2):
        utils.assertInstance(col1, SQLColumn)
        utils.assertInstance(col2, SQLColumn)
        self.jointype = QueryValidate.soft(str(jointype).lower())
        if self.jointype != "inner" and self.jointype != "left" and self.jointype != "right" and \
            self.jointype != "full outer":
            raise StandardError("Unknown join type %s" % jointype)
        if col1.table == col2.table:
            raise StandardError("Self-jons are not supported")
        self.conditions.append((jointype, col1, col2))
        return self

    def tables(self):
        tables = []
        for cond in self.conditions:
            tables.append(cond[0])
        return tables

class SQLOrder(QueryBasic):
    def __init__(self, col, ordertype):
        utils.assertInstance(col, SQLColumn)
        self.column = col
        self.ordertype = QueryValidate.strict(str(ordertype).lower())
        if self.ordertype != "desc" and self.ordertype != "asc":
            raise StandardError("Order type %s is unknown" % self.ordertype)

class SQLPredicate(QueryBasic):
    def __init__(self, col):
        utils.assertInstance(col, SQLColumn)
        self.column = col
        self.values = []
        self.expression = None

    def _simpleExpression(self, val, expression):
        self.values = [val]
        self.expression = "%s" % expression
        return self

    def eq(self, val):
        return self._simpleExpression(val, "=")

    def gt(self, val):
        return self._simpleExpression(val, ">")

    def lt(self, val):
        return self._simpleExpression(val, "<")

    def ge(self, val):
        return self._simpleExpression(val, ">=")

    def le(self, val):
        return self._simpleExpression(val, "<=")

    def isNull(self):
        return self._simpleExpression(None, "is")

    def between(val1, val2):
        self.values = [val1, val2]
        self.expression = "between"

    def isin(*vals):
        self.values = vals
        self.expression = "in"

class SQLPredicateGroup(QueryBasic):
    def __init__(self):
        self.group = []

    def AND(self, predicate):
        if isinstance(predicate, SQLPredicate):
            self.group.append(predicate)
        elif isinstance(predicate, SQLPredicateGroup):
            raise StandardError("Nested predicates are not supported")
        else:
            raise StandardError("Unknown predicate type %s" % type(predicate))

class Insert(QueryType):
    def __init__(self, table):
        utils.assertInstance(table, SQLTable)
        self.table = table
        self.command = QueryValidate.soft("INSERT INTO")

class Update(QueryType):
    def __init__(self, table):
        utils.assertInstance(table, SQLTable)
        self.table = table
        self.command = QueryValidate.soft("UPDATE")

class Delete(QueryType):
    def __init__(self, table):
        utils.assertInstance(table, SQLTable)
        self.table = table
        self.command = QueryValidate.soft("DELETE FROM")

class Select(QueryType):
    def __init__(self, table):
        self.table = table if isinstance(table, SQLTable) or isinstance(table, Join) else None
        if not self.table:
            raise StandardError("Table is not specified for Select query type")
        self.command = QueryValidate.soft("SELECT")

################################################################
# Partial query
################################################################
class PartialQuery(QueryBasic):
    def __init__(self):
        self.qtype = None
        self.columns = None
        self.values = None
        self.predicate = None
        self.groupby = None
        self.orderby = None
        self.limit = None

    def columns(self, *cols):
        # general error check
        if len(cols) == 0:
            raise StandardError("No columns specified")
        for col in cols:
            utils.assertInstance(col, SQLColumn)
        # resolve columns for each query type
        if isinstance(self.qtype, Insert) or isinstance(self.qtype, Update):
            # columns should belong to the table in qtype
            for col in cols:
                if col.table != self.qtype.table:
                    raise StandardError("Table %s does not have %s" % (table.uid, col.uid))
            self.columns = cols
        elif isinstance(self.qtype, Delete):
            raise StandardError("Delete query type requires no columns")
        elif isinstance(self.qtype, Select):
            # resolve select tables, it is either table or join
            entity = self.qtype.table
            tables = [table] if isinstance(entity, SQLTable) else entity.tables()
            for col in cols:
                if col.table not in tables:
                    raise StandardError("Column %s is not in any table" % col.uid)
            self.columns = cols
        else:
            raise StandardError("Undefined query type %s" % type(self.qtype))
        return self

    def values(self, *vals):
        if len(vals) == 0:
            raise StandardError("No values specified")
        if isinstance(self.qtype, Insert) or isinstance(self.qtype, Update):
            if not self.columns:
                raise StandardError("No columns specified")
            if len(vals) != len(self.columns):
                raise StandardError("%s values do not match %s columns" % (len(vals),
                    len(self.columns)))
            self.values = vals
        elif isinstance(self.qtype, Delete):
            raise StandardError("Delete query type requires no values")
        elif isinstance(self.qtype, Select):
            raise StandardError("Select query type requires no values")
        else:
            raise StandardError("Undefined query type %s" % type(self.qtype))
        return self

    def where(self, *predicates):
        if isinstance(self.qtype, Select) or isinstance(self.qtype, Update) or \
            isinstance(self.qtype, Delete):
            # operators supported: =, >, <, >=, <=, between, in
        elif isinstance(self.qtype, Insert):
            raise StandardError("Insert query type requires no predicate")
        else:
            raise StandardError("Undefined query type %s" % type(self.qtype))
        return self

    def groupBy(self, *groups):
        if isinstance(self.qtype, Select):
            # resolve select tables, it is either table or join
            entity = self.qtype.table
            tables = [table] if isinstance(entity, SQLTable) else entity.tables()
            for col in cols:
                if col.table not in tables:
                    raise StandardError("Column %s is not in any table" % col.uid)
            self.groupby = cols
        else:
            raise StandardError("Group By clause is only valid for Select query type")
        return self

    def orderBy(self, *orders):
        if isinstance(self.qtype, Select):
            if len(orders) == 0:
                raise StandardError("No order by columns specified")
            for order in orders:
                utils.assertInstance(order, SQLOrder)
            self.orderby = orders
        else:
            raise StandardError("Order By clause is only valid for Select query type")
        return self

    def limit(self, limit):
        utils.assertInstance(limit, IntType)
        if limit < 0:
            raise StandardError("Limit %s is negative" % limit)
        self.limit = limit
