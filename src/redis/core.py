#!/usr/bin/env python

# Octohaven core built for redis, later has to be generalized
import time
from src.redis.errors import CoreError
from types import FloatType

class User(object):
    def __init__(self, eid, name, email, created=time.time()):
        if type(created) is not FloatType:
            raise CoreError("[FloatType] required, passed [%s]"%(type(created)))
        self._id = str(eid)
        self._name = str(name)
        self._email = str(email)
        # created as a timestamp instance
        self._created = created

class Project(object):
    def __init__(self, eid, name, userid=None, created=time.time()):
        if type(created) is not FloatType:
            raise CoreError("[FloatType] required, passed [%s]"%(type(created)))
        self._id = str(eid)
        self._name = str(name)
        self._userid = str(userid) if userid else None
        # created as a timestamp instance
        self._created = created
