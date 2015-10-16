#!/usr/bin/env python

import json
from types import UnicodeType, StringType

# private decorator
def private(f):
    # This function is what we "replace" hello with
    def wrapper(*args, **kw):
        return f(*args, **kw)
    return wrapper

# getOrElse method for json
# raw is a string in json format, value is an alternative in case json fails
# we also convert all the string values from 'unicode' to 'str'
def jsonOrElse(raw, value):
    try:
        data = json.loads(raw)
        for key, value in data.items():
            newkey = str(key) if type(key) is UnicodeType else key
            newvalue = str(value) if type(value) is UnicodeType else value
            data[newkey] = newvalue
        return data
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