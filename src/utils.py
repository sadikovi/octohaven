#!/usr/bin/env python

import json, time, uuid
from datetime import datetime
from types import UnicodeType, StringType, DictType, ListType

# private decorator
def private(f):
    def wrapper(*args, **kw):
        return f(*args, **kw)
    return wrapper

# override decorator
def override(f):
    def wrapper(*args, **kw):
        return f(*args, **kw)
    return wrapper

# getOrElse method for json
# raw is a string in json format, value is an alternative in case json fails
# we also convert all the string values from 'unicode' to 'str'
def jsonOrElse(raw, value):
    # updates keys and values recursively to be Python `str`, if possible
    def utfKeys(obj):
        if type(obj) is ListType:
            return [utfKeys(x) for x in obj]
        elif type(obj) is DictType:
            updated = {}
            for key, value in obj.items():
                newkey = str(key) if type(key) is UnicodeType else key
                newvalue = utfKeys(value)
                updated[newkey] = newvalue
            return updated
        elif type(obj) is UnicodeType:
            return str(obj)
        else:
            return obj
    try:
        data = json.loads(raw)
        return utfKeys(data)
    except ValueError:
        return value

# getOrElse for integer, returns default, if cannot parse raw string
def intOrElse(raw, value):
    try:
        return int(raw)
    except ValueError:
        return value

# getOrElse for boolean, returns default, if cannot parse raw string
def boolOrElse(raw, value):
    try:
        pre = raw.lower()
        if pre == "true" or pre == "1" or pre == "yes":
            return True
        if pre == "false" or pre == "0" or pre == "no":
            return False
        return bool(pre)
    except ValueError:
        return value

# return current time in milliseconds
def currentTimeMillis():
    return long(time.time() * 1000.0)

# date to timestamp (in milliseconds) conversion
def dateToTimestamp(date):
    return (date - datetime(1970, 1, 1)).total_seconds() * 1000L

################################################################
# UID functions for model
################################################################
# create uid with prefix
def auid(prefix=""):
    return "%s" % prefix + uuid.uuid4().hex

# check that uid belongs to certain group
def isuid(uid, prefix):
    return type(uid) is StringType and uid.startswith(prefix)

# Job uid
def nextJobId():
    return auid("job_")

def isJobId(uid):
    return isuid(uid, "job_")

# Spark job uid
def nextSparkJobId():
    return auid("spark_")

def isSparkJobId(uid):
    return isuid(uid, "spark_")

# Template uid
def nextTemplateId():
    return auid("template_")

def isTemplateId(uid):
    return isuid(uid, "template_")

# Timetable uid
def nextTimetableId():
    return auid("timetable_")

def isTimetableId(uid):
    return isuid(uid, "timetable_")

################################################################
# Assertions
################################################################
# Helper method to check to type match
def assertType(passed, expected, msg=None):
    if type(passed) is not expected:
        msg = msg if msg else "Expected %s, got %s" % (expected, str(type(passed)))
        raise StandardError(msg)
    return True
