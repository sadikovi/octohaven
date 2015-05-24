#!/usr/bin/env python

from src.connector.redisconnector import RedisConnector
from src.redis.core import User, Project


class Manager(object):
    def __init__(self, connector):
        if type(connector) is not RedisConnector:
            raise StandardError("Connector is unknown")
        self._connector = connector

    def _userkey(self, uid):
        return "user:%s"%(uid)

    def _projectkey(self, uid, pid):
        return "user:%s#project:%s"%(uid, pid)

    def _user_conn_projectskey(self, uid):
        return "conn-projects#user:%s"%(uid)

    def getUser(self, uid):
        key = self._userkey(uid)
        info = self._connector.getObject(key)
        if not info:
            return None
        # convert into object
        _id = info["_id"]
        _name = info["_name"]
        _email = info["_email"]
        _created = info["_created"]
        return User(_id, _name, _email, _created)

    def createUser(self, uid, name, email):
        key = self._userkey(uid)
        user = User(uid, name, email)
        # convert into dict
        info = {}
        info["_id"] = user._id
        info["_name"] = user._name
        info["_email"] = user._email
        info["_created"] = user._created
        self._connector.storeObject(key, info)
        return user

    def getProject(self, uid, pid):
        key = self._projectkey(uid, pid)
        info = self._connector.getObject(key)
        if not info:
            return None
        _id = info["_id"]
        _name = info["_name"]
        _userid = info["_userid"]
        _created = info["_created"]
        return Project(_id, _name, _userid, _created)

    def createProject(self, uid, pid, name):
        key = self._projectkey(uid, pid)
        project = Project(pid, name, uid)
        # convert into object
        info = {}
        info["_id"] = project._id
        info["_name"] = project._name
        info["_userid"] = project._userid
        info["_created"] = project._created
        self._connector.storeObject(key, info)
        return project

    def addProjectForUser(self, uid, pid):
        key = self._user_conn_projectskey(uid)
        self._connector.storeConnection(key, pid)

    def projectsForUser(self, uid, asobject=False):
        key = self._user_conn_projectskey(uid)
        pids = self._connector.getConnection(key)
        if not pids:
            return None
        if asobject:
            return [self.getProject(uid, pid) for pid in pids if pid]
        else:
            return pids
