#!/usr/bin/env python

# Octohaven core built for redis, later has to be generalized
import time
from src.redis.errors import CoreError
from types import FloatType, DictType
import re
from datetime import datetime, timedelta

class User(object):
    def __init__(self, eid, name, email, created=time.time()):
        if type(created) is not FloatType:
            raise CoreError("[FloatType] required, passed [%s]"%(type(created)))
        self._id = str(eid)
        self._name = str(name)
        self._email = str(email)
        # created as a timestamp instance
        self._created = created

    @classmethod
    def create(cls, settings):
        if type(settings) is not DictType:
            raise CoreError("[DictType] required, passed [%s]"%(type(settings)))
        created = settings["_created"] if "_created" in settings else None
        return User(settings["_id"], settings["_name"], settings["_email"], created)

    def dict(self):
        return {
            "_id": self._id,
            "_name": self._name,
            "_email": self._email,
            "_created": self._created
        }

class Project(object):
    def __init__(self, eid, name, userid=None, created=time.time()):
        if type(created) is not FloatType:
            raise CoreError("[FloatType] required, passed [%s]"%(type(created)))
        if not Project.validateIdLength(eid):
            raise CoreError("Project id requires minimal length")
        if not Project.validateIdString(eid):
            raise CoreError("Project id can contain only letters, numbers and dashes")
        self._id = str(eid)
        self._name = str(name)
        self._userid = str(userid) if userid else None
        # created as a timestamp instance
        self._created = created

    def name(self):
        return self._name

    def id(self):
        return self._id

    def datetime(self, offset=None, template="%d/%m/%Y %H:%M:%S"):
        utc = datetime.utcfromtimestamp(self._created)
        local = (utc - timedelta(minutes=offset)) if offset else utc
        return local.strftime(template)

    @classmethod
    def create(cls, settings):
        if type(settings) is not DictType:
            raise CoreError("[DictType] required, passed [%s]"%(type(settings)))
        userid = settings["_userid"] if "_userid" in settings else None
        created = settings["_created"] if "_created" in settings else None
        return Project(settings["_id"], settings["_name"], userid, created)

    @staticmethod
    def validateIdLength(projectid):
        return len(projectid) >= 3

    @staticmethod
    def validateIdString(projectid):
        return bool(re.match("^[\w-]+$", projectid, re.I))

    def dict(self):
        return {
            "_id": self._id,
            "_name": self._name,
            "_userid": self._userid,
            "_created": self._created
        }
