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
                config.db_table_users_uniqueid: None,
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
    def createProject(self, userid, projectid):
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
                config.db_table_projects_userid: userid,
                config.db_table_projects_id: projectid,
                config.db_table_projects_created: datetime.now()
            },
            "predicate": {}
        }
        return self.connector.dml(execdata)

    def getProject(self, userid, projectid):
        projectid = Util.unifyid(projectid)
        # validation
        if not Util.checknumericid(userid) or not Util.checkid(projectid):
            return None
        # everything is ok, return project
        execdata = {
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_projects,
            "body": {
                config.db_table_projects_uniqueid: None,
                config.db_table_projects_userid: None,
                config.db_table_projects_id: None,
                config.db_table_projects_created: None
            },
            "predicate": {
                config.db_table_projects_userid: userid,
                config.db_table_projects_id: projectid
            }
        }
        return self.connector.sql(execdata)

    def deleteProject(self, userid, projectid):
        projectid = Util.unifyid(projectid)
        # validation
        if not Util.checknumericid(userid):
            raise StandardError("User id is incorrect")
        if not Util.checkid(projectid):
            raise StandardError("Project id is incorrect")
        execdata = {
            "type": "delete",
            "schema": config.db_schema,
            "table": config.db_table_projects,
            "body": {},
            "predicate": {
                config.db_table_projects_userid: userid,
                config.db_table_projects_id: projectid
            }
        }
        return self.connector.dml(execdata)

class BranchMetaStore(MetaStore):
    def createBranch(self, userid, projectid, branchid):
        branchid = Util.unifyid(branchid)
        # validation
        if not Util.checknumericid(projectid):
            raise StandardError("Project id is incorrect")
        if not Util.checknumericid(userid):
            raise StandardError("User id is incorrect")
        if not Util.checkid(branchid):
            raise StandardError("Branch id is incorrect")
        # create branch
        execdata = {
            "type": "insert",
            "schema": config.db_schema,
            "table": config.db_table_branches,
            "body": {
                config.db_table_branches_userid: userid,
                config.db_table_branches_projectid: projectid,
                config.db_table_branches_id: branchid,
                config.db_table_branches_created: datetime.now()
            },
            "predicate": {}
        }
        return self.connector.dml(execdata)

    def getBranch(self, userid, projectid, branchid):
        branchid = Util.unifyid(branchid)
        # validation
        if not (Util.checknumericid(userid) and Util.checknumericid(projectid)
                and Util.checkid(branchid)):
            return None
        # everything is ok, return branch
        execdata = {
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_branches,
            "body": {
                config.db_table_branches_uniqueid: None,
                config.db_table_branches_userid: None,
                config.db_table_branches_projectid: None,
                config.db_table_branches_id: None,
                config.db_table_branches_created: None
            },
            "predicate": {
                config.db_table_branches_userid: userid,
                config.db_table_branches_projectid: projectid,
                config.db_table_branches_id: branchid
            }
        }
        return self.connector.sql(execdata)

    def getBranchByUniqueId(self, uniquebranchid):
        if not Util.checknumericid(uniquebranchid):
            return None
        # everything is ok, return branch
        execdata = {
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_branches,
            "body": {
                config.db_table_branches_uniqueid: None,
                config.db_table_branches_userid: None,
                config.db_table_branches_projectid: None,
                config.db_table_branches_id: None,
                config.db_table_branches_created: None
            },
            "predicate": {
                config.db_table_branches_uniqueid: uniquebranchid
            }
        }
        return self.connector.sql(execdata)

    def deleteBranch(self, userid, projectid, branchid):
        branchid = Util.unifyid(branchid)
        # validation
        if not Util.checknumericid(userid):
            raise StandardError("User id is incorrect")
        if not Util.checknumericid(projectid):
            raise StandardError("Project id is incorrect")
        if not Util.checkid(branchid):
            raise StandardError("Branch id is incorrect")
        execdata = {
            "type": "delete",
            "schema": config.db_schema,
            "table": config.db_table_branches,
            "body": {},
            "predicate": {
                config.db_table_branches_userid: userid,
                config.db_table_branches_projectid: projectid,
                config.db_table_branches_id: branchid
            }
        }
        return self.connector.dml(execdata)

    def deleteBranchByUniqueId(self, uniquebranchid):
        if not Util.checknumericid(uniquebranchid):
            return None
        execdata = {
            "type": "delete",
            "schema": config.db_schema,
            "table": config.db_table_branches,
            "body": {},
            "predicate": {
                db_table_branches_uniqueid: uniquebranchid
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
    def createComponent(self, userid, id, type, fileurl):
        # prepare input data
        id, type, fileurl = Util.unifyid(id), type.strip(), fileurl.strip()
        if not Util.checknumericid(userid):
            raise StandardError("User id is incorrect")
        if not Util.checkid(id):
            raise StandardError("Component id is incorrect")
        # prepare execdata
        execdata = {
            "type": "insert",
            "schema": config.db_schema,
            "table": config.db_table_components,
            "body": {
                config.db_table_components_userid: userid,
                config.db_table_components_id: id,
                config.db_table_components_type: type,
                config.db_table_components_fileurl: fileurl,
                config.db_table_components_created: datetime.now()
            },
            "predicate": {}
        }
        return self.connector.dml(execdata)

    def getComponent(self, userid, id, type):
        id, type = Util.unifyid(id), type.strip()
        if not Util.checknumericid(userid) or not Util.checkid(id) or not type:
            return None
        execdata = {
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_components,
            "body": {
                config.db_table_components_unuqueid: None,
                config.db_table_components_userid: None,
                config.db_table_components_id: None,
                config.db_table_components_type: None,
                config.db_table_components_fileurl: None,
                config.db_table_components_created: None
            },
            "predicate": {
                config.db_table_components_userid: userid,
                config.db_table_components_id: id,
                config.db_table_components_type: type
            }
        }
        return self.connector.sql(execdata)

    def getComponentByUniqueId(self, componentid):
        if not Util.checknumericid(componentid):
            return None
        execdata = {
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_components,
            "body": {
                config.db_table_components_unuqueid: None,
                config.db_table_components_userid: None,
                config.db_table_components_id: None,
                config.db_table_components_type: None,
                config.db_table_components_fileurl: None,
                config.db_table_components_created: None
            },
            "predicate": {
                config.db_table_components_uniqueid: componentid
            }
        }
        return self.connector.sql(execdata)

    def deleteComponent(self, userid, id, type):
        id, type = Util.unifyid(id), type.strip()
        if not Util.checknumericid(userid):
            raise StandardError("User id is incorrect")
        if not Util.checkid(id):
            raise StandardError("Component id is incorrect")
        # prepare execdata
        execdata = {
            "type": "delete",
            "schema": config.db_schema,
            "table": config.db_table_components,
            "body": {},
            "predicate": {
                config.db_table_components_userid: userid,
                config.db_table_components_id: id,
                config.db_table_components_type: type
            }
        }
        return self.connector.dml(execdata)

    def deleteComponentByUniqueId(self, componentid):
        if not Util.checknumericid(componentid):
            return None
        # prepare execdata
        execdata = {
            "type": "delete",
            "schema": config.db_schema,
            "table": config.db_table_components,
            "body": {},
            "predicate": {
                config.db_table_components_uniqueid: componentid
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

    def createComponentRevision(self):
        pass
