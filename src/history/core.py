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

    @staticmethod
    def randomkey():
        return uuid.uuid4().hex

class User(object):
    def __init__(self, eid, name, email, created=None):
        self._id = str(eid).lower()
        self._name = str(name)
        self._email = str(email)
        # created as a timestamp instance
        self._created = created or time.time()
        if type(self._created) is not FloatType:
            raise CoreError("[FloatType] required, passed [%s]"%(type(self._created)))
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
    def __init__(self, _hash, name, desc, created=None):
        self._hash = _hash if _hash else Key.randomkey()
        self._name = Project.validateName(name)
        self._desc = str(desc) if desc else ""
        self._created = created or time.time()

    @staticmethod
    def MIN_NAME_LENGTH():
        return 6

    @staticmethod
    def NAME_REGEXP(closed=True):
        a = "[\w-]+"
        return "^%s$"%(a) if closed else a

    def hash(self):
        return self._hash

    def name(self):
        return self._name

    def setDesc(self, desc):
        self._desc = desc.strip()

    def desc(self):
        return self._desc

    def created(self):
        return self._created

    def datetime(self, offset=None, template="%d/%m/%Y %H:%M:%S"):
        utc = datetime.utcfromtimestamp(self._created)
        local = (utc - timedelta(minutes=offset)) if offset else utc
        return local.strftime(template)

    @classmethod
    def create(cls, settings):
        if type(settings) is not DictType:
            raise CoreError("[DictType] required, passed [%s]"%(type(settings)))
        desc = settings["_desc"] if "_desc" in settings else None
        created = settings["_created"] if "_created" in settings else None
        return Project(settings["_hash"], settings["_name"], desc, created)

    @staticmethod
    def validateName(name):
        if not name:
            raise CoreError("Project name is not specified")
        if len(name) < Project.MIN_NAME_LENGTH():
            raise CoreError("Project name must be at least %d characters long"%(Project.MIN_NAME_LENGTH()))
        if not bool(re.match(Project.NAME_REGEXP(), name, re.I)):
            raise CoreError("Project name can contain only letters, numbers and dashes")
        return str(name).strip().lower()

    def dict(self):
        return {
            "_hash": self._hash,
            "_name": self._name,
            "_desc": self._desc,
            "_created": self._created
        }

class ProjectGroup(object):
    def __init__(self, key):
        self._rediskey = key
        self._projects = {}
        self._removed = []

    def key(self):
        return self._rediskey

    def fill(self, project):
        if type(project) is not Project:
            raise CoreError("[Project] required, [%s] passed"%(type(project)))
        self._projects[project.name()] = project

    def addProject(self, name, desc):
        if name in self._projects:
            raise CoreError("Project {%s} already exists"%(name))
        self._projects[name] = Project(None, name, desc)

    def removeProject(self, name):
        if name not in self._projects:
            raise CoreError("Project {%s} is not recognized"%(name))
        self._removed.append(self._projects[name].hash())
        del self._projects[name]

    def updateDesc(self, name, desc):
        if name not in self._projects:
            raise CoreError("Project {%s} is not recognized"%(name))
        self._projects[name].setDesc(desc)

    def project(self, name, asdict=False):
        if name not in self._projects:
            return None
        a = self._projects[name]
        return a.dict() if asdict else a

    def projects(self, asdict=False):
        a = self._projects.values()
        return a if not asdict else [x.dict() for x in a]

class Branch(object):
    def __init__(self, _hash, name, created=None, edited=None, default=False):
        self._hash = _hash if _hash else Key.randomkey()
        self._name = Branch.validateName(name)
        self._created = created or time.time()
        self._edited = edited or time.time()
        self._default = bool(default)

    @classmethod
    def create(cls, settings):
        if type(settings) is not DictType:
            raise CoreError("[DictType] required, passed [%s]"%(type(settings)))
        created = settings["_created"] if "_created" in settings else None
        edited = settings["_edited"] if "_edited" in settings else None
        default = settings["_default"] if "_default" in settings else None
        return Branch(settings["_hash"], settings["_name"], created, edited, default)

    @staticmethod
    def validateName(name):
        if not name:
            raise CoreError("Branch name is not specified")
        return str(name).strip().lower()

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

    def setDefault(self, flag):
        self._default = flag
        self._edited = time.time()

    def dict(self):
        return {
            "_hash": self._hash,
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
        self._branches[branchname] = Branch(None, branchname)

    def removeBranch(self, branchname):
        if branchname not in self._branches:
            raise CoreError("Branch {%s} is unrecognized"%(branchname))
        self._removed.append(self._branches[branchname].hash())
        del self._branches[branchname]

    def setDefault(self, branchname):
        if branchname not in self._branches:
            raise CoreError("Branch {%s} is unrecognized"%(branchname))
        for k, v in self._branches.items():
            v._default = False
        self._branches[branchname].setDefault(True)

    def branches(self, asdict=False):
        a = self._branches.values()
        return a if not asdict else [x.dict() for x in a]

    def branch(self, bname, asdict=False):
        if bname in self._branches:
            branch = self._branches[bname]
            return branch if not asdict else branch.dict()
        return None

    def default(self):
        if not self._branches:
            return None
        a = [x for x in self._branches.values() if x._default]
        if len(a) != 1:
            firstbranch = self._branches.values()[0]
            self.setDefault(firstbranch.name())
