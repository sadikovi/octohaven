#!/usr/bin/env python

import json, time
import uuid
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

# UID functions for model
def nextJobId():
    return "job_" + uuid.uuid4().hex

def nextSparkJobId():
    return "spark_" + uuid.uuid4().hex

def nextTemplateId():
    return "template_" + uuid.uuid4().hex

def nextTimetableId():
    return "timetable_" + uuid.uuid4().hex
