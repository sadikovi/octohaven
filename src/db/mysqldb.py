import src.config as config
import mysql.connector

cnx = mysql.connector.connect(user=config.mysql_user, password=config.mysql_pass, host=config.mysql_host, database=config.db_schema)

def _insert(cursor, payload):
    schema, table = payload.schema, payload.table
    keys, values = [], []
    for key, value in payload.data.items():
        keys.append("%s" %(key))
        values.append("%(%s)s" %(key))
    metaquery = "insert into %s.%s (%s) values (%s)" % (schema, table, ", ".join(keys), ", ".join(values))
    cursor.execute(metaquery, payload.data)

def _delete(cursor, data):
    schema, table = payload.schema, payload.table
    pairs = []
    for key, value in payload.data.items():
        pairs.append("%s = %(%s)s" %(key, key))
    metaquery = "delete from %s.%s where (%s)" % (schema, table, " and ".join(pairs))
    cursor.execute(metaquery, payload.data)

def _select(cursor, data):
    pass

def insert(payload):
    cnx.connect()
    cursor = cnx.cursor()
    # run command
    _insert(cursor, payload)
    # commit
    cnx.commit()
    cursor.close()
    cnx.close()

def delete(payload):
    cnx.connect()
    cursor = cnx.cursor()
    # run command
    _delete(cursor, payload)
    # commit
    cnx.commit()
    cursor.close()
    cnx.close()

def select(payload):
    pass
