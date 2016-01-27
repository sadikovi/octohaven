#!/usr/bin/env python

#
# Copyright 2015 sadikovi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os, re, json, time
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

# getOrElse for integer, returns default, if cannot parse raw string, or object
def intOrElse(raw, value):
    try:
        return int(raw)
    except (ValueError, TypeError):
        return value

# getOrElse for boolean, returns default, if cannot parse raw string, or object
def boolOrElse(raw, value):
    try:
        pre = raw.lower()
        if pre == "true" or pre == "1" or pre == "yes":
            return True
        if pre == "false" or pre == "0" or pre == "no":
            return False
        return bool(pre)
    except (ValueError, TypeError):
        return value

# return current time in milliseconds
def currentTimeMillis():
    return long(time.time() * 1000.0)

# date to timestamp (in milliseconds) conversion
def dateToTimestamp(date):
    return (date - datetime(1970, 1, 1)).total_seconds() * 1000L

################################################################
# Assertions
################################################################
# Helper method to check to type match
def assertType(passed, expected, msg=None):
    if type(passed) is not expected:
        msg = msg if msg else "Expected %s, got %s" % (expected, str(type(passed)))
        raise StandardError(msg)
    return True

# Assert instance on subclasses
def assertInstance(passed, expectedType, msg=None):
    if not isinstance(passed, expectedType):
        msg = msg if msg else "Instance %s is not of type %s" % (passed, str(expectedType))
        raise StandardError(msg)
    return True

################################################################
# Checks for urls, statuses, etc.
################################################################
# Try parsing regular expression, raise Error, if parsing fails.
# Return groups of parsed data
def _parseRe(regexp, value, msg_on_failure=None):
    groups = re.match(regexp, value)
    if groups is None:
        msg = "Failed to parse" if not msg_on_failure else msg_on_failure % value
        raise StandardError(msg)
    return groups

def validateMemory(value):
    return _parseRe(r"^(\d+)(k|kb|m|mb|g|gb|t|tb|p|pb)$", value.lower(),
        "Memory is incorrect: %s").group(0)

def validatePriority(value):
    wrapped = intOrElse(value, -1)
    if wrapped < 0:
        raise StandardError("Priority is incorrect: %s" % value)
    return value

# if "as_uri_parts" is True, returns result as tuple (uri, host, port)
def validateMasterUrl(masterurl, as_uri_parts=False):
    groups = _parseRe(r"^spark://([\w\.-]+):(\d+)$", masterurl, "Spark Master URL is incorrect: %s")
    if as_uri_parts:
        host = groups.group(1)
        port = int(groups.group(2))
        return (masterurl, host, port)
    else:
        return masterurl

# if "as_uri_parts" is True, returns result as tuple (uri, host, port)
def validateUiUrl(uiurl, as_uri_parts=False):
    groups = _parseRe(r"^http(s)?://([\w\.-]+):(\d+)$", uiurl, "Spark UI URL is incorrect: %s")
    if as_uri_parts:
        host = groups.group(2)
        port = int(groups.group(3))
        return (uiurl, host, port)
    else:
        return uiurl

def validateEntrypoint(entrypoint):
    return _parseRe(r"^(\w+)(\.\w+)*$", entrypoint, "Entrypoint is incorrect: %s").group(0)

def validateJarPath(jar):
    # do not validate on existence, only on path structure
    ok = os.path.isabs(jar) and jar.lower().endswith(".jar")
    if not ok:
        raise StandardError("Path %s is not valid" % jar)
    return jar
