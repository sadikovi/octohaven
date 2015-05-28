#!/usr/bin/env python

from src.connector.redisconnector import RedisConnector
from src.redis.core import User, Project, Branch, BranchGroup


class Manager(object):
    def __init__(self, connector):
        if type(connector) is not RedisConnector:
            raise StandardError("Connector is unknown")
        self._connector = connector

    # keys
    def _userkey(self, uid):
        return "user:%s"%(uid)

    def _projectkey(self, hashkey, pid):
        return "user:%s#project:%s"%(hashkey, pid)

    def _user_conn_projectskey(self, hashkey):
        return "conn-projects#user:%s"%(hashkey)

    def _branchgroupkey(self, userhash, projecthash):
        return "user:%s#project:%s#branchgroup"%(userhash, projecthash)

    def _branchkey(self, branchgroupkey, branchid):
        return "%s#branch:%s"%(branchgroupkey, branchid)

    ##################################
    # User
    ##################################

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

    def deleteUser(self, uid):
        key = self._userkey(uid)
        self._connector.delete(key)

    ##################################
    # Project
    ##################################

    def createProject(self, hashkey, pid, name):
        key = self._projectkey(hashkey, pid)
        project = Project(pid, name)
        self._connector.storeObject(key, project.dict())
        return project

    def getProject(self, hashkey, pid):
        key = self._projectkey(hashkey, pid)
        info = self._connector.getObject(key)
        return Project.create(info) if info else None

    def updateProject(self, hashkey, pid, name):
        proj = self.getProject(hashkey, pid)
        if proj:
            proj.setName(name)
            # update proj
            key = self._projectkey(hashkey, pid)
            self._connector.storeObject(key, proj.dict())
        return proj

    ##################################
    # Project - User connections
    ##################################

    def addProjectForUser(self, hashkey, pid):
        key = self._user_conn_projectskey(hashkey)
        self._connector.storeConnection(key, pid)

    def removeProjectForUser(self, hashkey, pid):
        key = self._user_conn_projectskey(hashkey)
        self._connector.removeConnection(key, pid)

    def projectsForUser(self, hashkey, asobject=False):
        key = self._user_conn_projectskey(hashkey)
        pids = self._connector.getConnection(key)
        if not pids:
            return None
        a = [x for x in pids if x]
        if asobject:
            b = [self.getProject(hashkey, pid) for pid in a]
            a = [x for x in b if x]
        return a

    ##################################
    # Branch group
    ##################################

    def getBranchGroup(self, userhash, projecthash):
        key = self._branchgroupkey(userhash, projecthash)
        bids = self._connector.getConnection(key)
        branchgroup = BranchGroup(key)
        if bids:
            for bid in bids:
                bkey = self._branchkey(key, bid)
                info = self._connector.getObject(bkey)
                if info:
                    branchgroup.fill(Branch.create(info))
            branchgroup.default()
        return branchgroup

    def updateBranchGroup(self, branchgroup):
        key = branchgroup.key()
        bids = self._connector.getConnection(key)
        # remove deleted keys
        self._connector.removeConnection(key, *branchgroup._removed)
        # update valid keys
        for branch in branchgroup.branches():
            bkey = self._branchkey(key, branch.name())
            self._connector.storeObject(bkey, branch.dict())
            self._connector.storeConnection(key, branch.name())
        branchgroup.default()
        return branchgroup
