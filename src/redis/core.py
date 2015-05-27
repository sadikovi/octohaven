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
        self._id = str(eid).lower()
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

    def id(self):
        return self._id

class Project(object):
    def __init__(self, eid, name, userid=None, created=time.time()):
        if type(created) is not FloatType:
            raise CoreError("[FloatType] required, passed [%s]"%(type(created)))
        if not Project.validateIdLength(eid):
            raise CoreError("Project id must be at least %d characters long"%(Project.MIN_ID_LENGTH()))
        if not Project.validateIdString(eid):
            raise CoreError("Project id can contain only letters, numbers and dashes")
        self._id = str(eid).lower()
        self._name = str(name)
        self._userid = str(userid) if userid else None
        # created as a timestamp instance
        self._created = created

    @staticmethod
    def MIN_ID_LENGTH():
        return 6

    @staticmethod
    def ID_REGEXP(closed=True):
        a = "[\w-]+"
        return "^%s$"%(a) if closed else a

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name.strip()

    def id(self):
        return self._id

    def userid(self):
        return self._userid

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
        return len(projectid) >= Project.MIN_ID_LENGTH()

    @staticmethod
    def validateIdString(projectid):
        return bool(re.match(Project.ID_REGEXP(), projectid, re.I))

    def dict(self):
        return {
            "_id": self._id,
            "_name": self._name,
            "_userid": self._userid,
            "_created": self._created
        }
