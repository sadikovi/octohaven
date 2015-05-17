#!/usr/bin/env python

import src.config as config
from src.connector.mysqlconnector import MySqlConnector
from datetime import datetime
from types import StringType, IntType
import re

class Util(object):
    @staticmethod
    def checkid(someid):
        return someid and re.match("^[\w-]+$", someid, re.I)
    @staticmethod
    def checknumericid(someid):
        return type(someid) is IntType and someid > 0
    @staticmethod
    def unifyid(someid):
        return ("%s"%(someid)).strip().lower()

# TODO: !!! optimisation of the workflow and validation
class MetaStore(object):
    def __init__(self, connector):
        if not connector or type(connector) is not MySqlConnector:
            raise StandardError("Wrong connector")
        self.connector = connector

class UserMetaStore(MetaStore):
    def createUser(self, userid):
        userid = Util.unifyid(userid)
        # validate fields
        if not Util.checkid(userid):
            raise StandardError("User id is incorrect")
        if self.userExists(userid):
            raise StandardError("User name is already taken")
        # prepare execdata
        execdata = {
            "type": "insert",
            "schema": config.db_schema,
            "table": config.db_table_users,
            "body": {
                config.db_table_users_id: userid,
                config.db_table_users_created: datetime.now()
            },
            "predicate": {}
        }
        return self.connector.dml(execdata)

    def getUser(self, userid):
        userid = Util.unifyid(userid)
        if not Util.checkid(userid):
            return None
        # prepare execdata
        execdata = {
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_users,
            "body": {
                config.db_table_users_id: None,
                config.db_table_users_created: None
            }
            "predicate": {
                config.db_table_users_id: userid
            }
        }
        return self.connector.sql(execdata)

    def userExists(self, userid):
        return True and self.getUser(userid)

    def deleteUser(self, userid):
        userid = Util.unifyid(userid)
        if not Util.checkid(userid):
            return False
        # prepare execdata
        execdata = {
            "type": "delete"
            "schema": config.db_schema,
            "table": config.db_table_users,
            "body": {},
            "predicate": {
                config.db_table_users_id: userid
            }
        }
        return self.connector.dml(execdata)

class ProjectMetaStore(MetaStore):
    def createProject(self, projectid, userid):
        projectid, userid = Util.unifyid(projectid), Util.unifyid(userid)
        # validation
        if not Util.checkid(userid):
            raise StandardError("User id is incorrect")
        if not Util.checkid(projectid):
            raise StandardError("Project id is incorrect")
        # create project
        execdata = {
            "type": "insert",
            "schema": config.db_schema,
            "table": config.db_table_projects,
            "body": {
                config.db_table_projects_id: projectid,
                config.db_table_projects_userid: userid,
                config.db_table_projects_created: datetime.now()
            },
            "predicate": {}
        }
        return self.connector.dml(execdata)

    def getProject(self, projectid, userid):
        projectid, userid = Util.unifyid(projectid), Util.unifyid(userid)
        # validation
        if not Util.checkid(userid) or not Util.checkid(projectid):
            return None
        # everything is ok, return project
        execdata = {
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_projects,
            "body": {
                config.db_table_projects_id: None,
                config.db_table_projects_userid: None,
                config.db_table_projects_created: None
            },
            "predicate": {
                config.db_table_projects_id: projectid,
                config.db_table_projects_userid: userid
            }
        }
        return self.connector.sql(execdata)

    def deleteProject(self, projectid, userid):
        projectid, userid = Util.unifyid(projectid), Util.unifyid(userid)
        # validation
        if not Util.checkid(userid):
            raise StandardError("User id is incorrect")
        if not Util.checkid(projectid):
            raise StandardError("Project id is incorrect")
        execdata = {
            "type": "delete",
            "schema": config.db_schema,
            "table": config.db_table_projects,
            "body": {},
            "predicate": {
                config.db_table_projects_id: projectid,
                config.db_table_projects_userid: userid
            }
        }
        return self.connector.dml(execdata)

class BranchMetaStore(MetaStore):
    def createBranch(self, projectid, userid, branchid):
        projectid = Util.unifyid(projectid)
        userid = Util.unifyid(userid)
        branchid = Util.unifyid(branchid)
        # validation
        if not Util.checkid(projectid):
            raise StandardError("Project id is incorrect")
        if not Util.checkid(userid):
            raise StandardError("User id is incorrect")
        if not Util.checkid(branchid):
            raise StandardError("Branch id is incorrect")
        # create branch
        execdata = {
            "type": "insert",
            "schema": config.db_schema,
            "table": config.db_table_branches,
            "body": {
                config.db_table_branches_projectid: projectid,
                config.db_table_branches_userid: userid,
                config.db_table_branches_id: branchid,
                config.db_table_branches_created: datetime.now()
            },
            "predicate": {}
        }
        return self.connector.dml(execdata)

    def getBranch(self, projectid, userid, branchid):
        projectid = Util.unifyid(projectid)
        userid = Util.unifyid(userid)
        branchid = Util.unifyid(branchid)
        # validation
        if not (Util.checkid(userid) and Util.checkid(projectid)
                and Util.checkid(branchid)):
            return None
        # everything is ok, return branch
        execdata = {
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_branches,
            "body": {
                config.db_table_branches_branchid: None,
                config.db_table_branches_projectid: None,
                config.db_table_branches_userid: None,
                config.db_table_branches_id: None,
                config.db_table_branches_created: None
            },
            "predicate": {
                config.db_table_branches_projectid: projectid,
                config.db_table_branches_userid: userid,
                config.db_table_branches_id: branchid
            }
        }
        return self.connector.sql(execdata)

    def getBranch(self, uniquebranchid):
        if not Util.checknumericid(uniquebranchid):
            return None
        # everything is ok, return branch
        execdata = {
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_branches,
            "body": {
                config.db_table_branches_branchid: None,
                config.db_table_branches_projectid: None,
                config.db_table_branches_userid: None,
                config.db_table_branches_id: None,
                config.db_table_branches_created: None
            },
            "predicate": {
                config.db_table_branches_branchid: uniquebranchid
            }
        }
        return self.connector.sql(execdata)

    def deleteBranch(self, projectid, userid, branchid):
        projectid = Util.unifyid(projectid)
        userid = Util.unifyid(userid)
        branchid = Util.unifyid(branchid)
        # validation
        if not Util.checkid(userid):
            raise StandardError("User id is incorrect")
        if not Util.checkid(projectid):
            raise StandardError("Project id is incorrect")
        if not Util.checkid(branchid):
            raise StandardError("Branch id is incorrect")
        execdata = {
            "type": "delete",
            "schema": config.db_schema,
            "table": config.db_table_branches,
            "body": {},
            "predicate": {
                config.db_table_branches_projectid: projectid,
                config.db_table_branches_userid: userid,
                config.db_table_branches_id: branchid
            }
        }
        return self.connector.dml(execdata)

    def deleteBranch(self, uniquebranchid):
        if not Util.checknumericid(uniquebranchid):
            return None
        execdata = {
            "type": "delete",
            "schema": config.db_schema,
            "table": config.db_table_branches,
            "body": {},
            "predicate": {
                db_table_branches_branchid: uniquebranchid
            }
        }
        return self.connector.dml(execdata)

class ModuleMetaStore(MetaStore):
    def createModule(self):
        execdata = {
            "type": "insert",
            "schema": config.db_schema,
            "table": config.db_table_modules,
            "body": {
                config.db_table_modules_created: datetime.now()
            },
            "predicate": {}
        }
        return self.connector.dml(execdata)

    def getModule(self, moduleid):
        if not Util.checknumericid(moduleid):
            return None
        execdata = {
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_modules,
            "body": {
                config.db_table_modules_id: None,
                config.db_table_modules_created: None
            },
            "predicate": {
                config.db_table_modules_id: moduleid
            }
        }
        return self.connector.sql(execdata)

# TODO: check components module
class ComponentMetaStore(MetaStore):
    def createComponent(self, name, type, fileurl, extension, desc):
        # prepare input data
        name = name.strip()
        type = type.strip()
        fileurl = fileurl.strip()
        extension = extension.strip()
        desc = desc.strip()
        # prepare execdata
        execdata = {
            "type": "insert",
            "schema": config.db_schema,
            "table": config.db_table_components,
            "body": {
                config.db_table_components_name: name,
                config.db_table_components_type: type,
                config.db_table_components_fileurl: fileurl,
                config.db_table_components_extension: extension,
                config.db_table_components_description: desc,
                config.db_table_components_created: datetime.now(),
            },
            "predicate": {}
        }
        return self.connector.dml(execdata)

    def getComponentVersions(self, name, onlylatest=True):
        name = name.strip()
        execdata = {
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_components,
            "body": {
                config.db_table_components_revision_id: None,
                config.db_table_components_name: None,
                config.db_table_components_type: None,
                config.db_table_components_fileurl: None,
                config.db_table_components_extension: None,
                config.db_table_components_description: None,
                config.db_table_components_created: None,
                config.db_table_components_latest: None
            },
            "predicate": {
                config.db_table_components_name: name,
                config.db_table_components_latest: 1
            }
        }
        return self.connector.sql(execdata, fetchone=onlylatest)

    def deleteComponent(self, name):
        name = name.strip()
        execdata = {
            "type": "delete",
            "schema": config.db_schema,
            "table": config.db_table_components,
            "body": {},
            "predicate": {
                db_table_components_name: name
            }
        }
        return self.connector.dml(execdata)

class RevisionMaster(MetaStore):
    def createBranchRevision(self, uniquebranchid):
        pass

    def createModuleRevision(self, moduleid):
        pass

    def createBranchModuleChain(self, branchid, moduleid):
        pass
