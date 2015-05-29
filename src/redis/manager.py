#!/usr/bin/env python

from src.connector.redisconnector import RedisConnector
from src.redis.core import User, Project, Branch, BranchGroup, ProjectGroup


class Manager(object):
    def __init__(self, connector):
        if type(connector) is not RedisConnector:
            raise StandardError("Connector is unknown")
        self._connector = connector

    # keys
    def _userkey(self, uid):
        return "user:%s"%(uid)

    def _projectgroupkey(self, userhash):
        return "user:%s#projectgroup"%(userhash)

    def _projectkey(self, projectgroupkey, projecthash):
        return "%s#project:%s"%(projectgroupkey, projecthash)


    def _branchgroupkey(self, userhash, projecthash):
        return "user:%s#project:%s#branchgroup"%(userhash, projecthash)

    def _branchkey(self, branchgroupkey, branchhash):
        return "%s#branch:%s"%(branchgroupkey, branchhash)

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
    # Project group
    ##################################

    def getProjectGroup(self, userhash):
        key = self._projectgroupkey(userhash)
        pkeys = self._connector.getConnection(key)
        projectgroup = ProjectGroup(key)
        if pkeys:
            for pkey in pkeys:
                info = self._connector.getObject(pkey)
                if info:
                    projectgroup.fill(Project.create(info))
        return projectgroup

    def updateProjectGroup(self, projectgroup):
        key = projectgroup.key()
        # remove deleted keys
        self._connector.removeConnection(
            key,
            *[self._projectkey(key, x) for x in projectgroup._removed]
        )
        # update valid keys
        for project in projectgroup.projects():
            pkey = self._projectkey(key, project.hash())
            self._connector.storeObject(pkey, project.dict())
            self._connector.storeConnection(key, pkey)
        return projectgroup

    ##################################
    # Branch group
    ##################################

    def getBranchGroup(self, userhash, projecthash):
        key = self._branchgroupkey(userhash, projecthash)
        bkeys = self._connector.getConnection(key)
        branchgroup = BranchGroup(key)
        if bkeys:
            for bkey in bkeys:
                info = self._connector.getObject(bkey)
                if info:
                    branchgroup.fill(Branch.create(info))
            branchgroup.default()
        return branchgroup

    def updateBranchGroup(self, branchgroup):
        key = branchgroup.key()
        # remove deleted keys
        self._connector.removeConnection(
            key,
            *[self._branchkey(key, x) for x in branchgroup._removed]
        )
        # update valid keys
        for branch in branchgroup.branches():
            bkey = self._branchkey(key, branch.hash())
            self._connector.storeObject(bkey, branch.dict())
            self._connector.storeConnection(key, bkey)
        branchgroup.default()
        return branchgroup
