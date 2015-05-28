#!/usr/bin/env python

# Octohaven core built for redis, later has to be generalized
import time
from src.redis.errors import CoreError
from types import FloatType, DictType
import re
from datetime import datetime, timedelta
import uuid

class Key(object):
    @staticmethod
    def hashkey(eid, created):
        combo = "%s#%s"%(eid, created)
        return uuid.uuid3(uuid.NAMESPACE_DNS, combo).hex

class User(object):
    def __init__(self, eid, name, email, created=time.time()):
        if type(created) is not FloatType:
            raise CoreError("[FloatType] required, passed [%s]"%(type(created)))
        self._id = str(eid).lower()
        self._name = str(name)
        self._email = str(email)
        # created as a timestamp instance
        self._created = created
        # create hash for projects
        self._hash = Key.hashkey(self._id, self._created)

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

    def hash(self):
        return self._hash

class Project(object):
    def __init__(self, eid, name, created=time.time()):
        if type(created) is not FloatType:
            raise CoreError("[FloatType] required, passed [%s]"%(type(created)))
        if not eid:
            raise CoreError("Project must have an id")
        # stringify id and lower
        self._id = str(eid).lower()
        # validate id
        if not Project.validateIdLength(self._id):
            raise CoreError("Project id must be at least %d characters long"%(Project.MIN_ID_LENGTH()))
        if not Project.validateIdString(self._id):
            raise CoreError("Project id can contain only letters, numbers and dashes")
        # assign other parameters
        self._name = str(name) if name else ""
        # created as a timestamp instance
        self._created = created
        # create hash for branches
        self._hash = Key.hashkey(self._id, self._created)

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

    def hash(self):
        return self._hash

    def datetime(self, offset=None, template="%d/%m/%Y %H:%M:%S"):
        utc = datetime.utcfromtimestamp(self._created)
        local = (utc - timedelta(minutes=offset)) if offset else utc
        return local.strftime(template)

    @classmethod
    def create(cls, settings):
        if type(settings) is not DictType:
            raise CoreError("[DictType] required, passed [%s]"%(type(settings)))
        created = settings["_created"] if "_created" in settings else None
        return Project(settings["_id"], settings["_name"], created)

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
            "_created": self._created
        }

class Branch(object):
    def __init__(self, name, created=time.time(), edited=time.time(), default=False):
        self._name = str(name).strip()
        self._created = created
        self._edited = edited
        self._default = bool(default)
        self._hash = Key.hashkey(self._name, self._created)

    @classmethod
    def create(cls, settings):
        if type(settings) is not DictType:
            raise CoreError("[DictType] required, passed [%s]"%(type(settings)))
        created = settings["_created"] if "_created" in settings else None
        edited = settings["_edited"] if "_edited" in settings else None
        default = settings["_default"] if "_default" in settings else None
        return Branch(settings["_name"], created, edited, default)

    def name(self):
        return self._name

    def hash(self):
        return self._hash

    def created(self):
        return self._created

    def edited(self):
        return self._edited

    def default(self):
        return self._default

    def dict(self):
        return {
            "_name": self._name,
            "_created": self._created,
            "_edited": self._edited,
            "_default": self._default
        }

class BranchGroup(object):
    def __init__(self, key):
        self._rediskey = key
        self._branches = {}
        self._removed = []

    def key(self):
        return self._rediskey

    # [!] for managing only
    def fill(self, branch):
        if type(branch) is not Branch:
            raise CoreError("[Branch] is required, [%s] passed"%(type(branch)))
        self._branches[branch.name()] = branch

    def addBranch(self, branchname):
        if branchname in self._branches:
            raise CoreError("Branch {%s} already exists"%(branchname))
        self._branches[branchname] = Branch(branchname)

    def removeBranch(self, branchname):
        print branchname, self._branches
        if branchname not in self._branches:
            raise CoreError("Branch {%s} is unrecognized"%(branchname))
        self._removed.append(branchname)
        del self._branches[branchname]

    def setDefault(self, branchname):
        if branchname not in self._branches:
            raise CoreError("Branch {%s} is unrecognized"%(branchname))
        for k, v in self._branches.items():
            v._default = False
        self._branches[branchname]._default = True

    def branches(self, asdict=False):
        a = self._branches.values()
        return a if not asdict else [x.dict() for x in a]

    def branch(self, bname, asdict=False):
        if branchname in self._branches:
            branch = self._branches[branchname]
            return branch if not asdict else branch.dict()
        return None

    def default(self):
        if not self._branches:
            return None
        a = [x for x in self._branches.values() if x._default]
        if len(a) != 1:
            firstbranch = self._branches.values()[0]
            self.setDefault(firstbranch.name())
