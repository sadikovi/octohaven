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
        return User.create(info)

    def createUser(self, uid, name, email):
        key = self._userkey(uid)
        user = User(uid, name, email)
        # convert into dict
        self._connector.storeObject(key, user.dict())
        return user

    def getProject(self, uid, pid):
        key = self._projectkey(uid, pid)
        info = self._connector.getObject(key)
        if not info:
            return None
        return Project.create(info)

    def createProject(self, uid, pid, name):
        key = self._projectkey(uid, pid)
        project = Project(pid, name, uid)
        # convert into object
        self._connector.storeObject(key, project.dict())
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
