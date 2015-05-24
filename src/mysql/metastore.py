#!/usr/bin/env python

import src.mysql.config as config
from src.connector.mysqlconnector import MySqlConnector, Query
from datetime import datetime
from types import StringType, IntType
import re

class Util(object):
    @staticmethod
    def checkid(someid):
        return type(someid) is StringType and bool(re.match("^[\w-]+$", someid, re.I))
    @staticmethod
    def checknumericid(someid):
        return type(someid) is IntType and someid > 0
    @staticmethod
    def unifyid(someid):
        return ("%s"%(someid)).strip().lower()

class MetaStore(object):
    def __init__(self, connector):
        if not connector or type(connector) is not MySqlConnector:
            raise StandardError("Wrong connector")
        self.connector = connector

class UserMetaStore(MetaStore):
    def createUser(self, userid, userpass):
        userid = Util.unifyid(userid)
        # validate fields
        if not Util.checkid(userid):
            raise StandardError("User id is incorrect")
        if self.userExists(userid):
            raise StandardError("User name is already taken")
        # prepare execdata
        return self.connector.dml({
            "type": "insert",
            "schema": config.db_schema,
            "table": config.db_table_users,
            "body": {
                config.db_table_users_id: userid,
                config.db_table_users_pass: userpass,
                config.db_table_users_created: datetime.now()
            },
            "predicate": {}
        })

    def getUser(self, userid):
        userid = Util.unifyid(userid)
        if not Util.checkid(userid):
            return None
        # prepare execdata
        return self.connector.sql({
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_users,
            "body": {
                config.db_table_users_uniqueid: None,
                config.db_table_users_id: None,
                config.db_table_users_pass: None,
                config.db_table_users_created: None
            },
            "predicate": {
                config.db_table_users_id: userid
            }
        })

    def userExists(self, userid):
        return bool(self.getUser(userid))

    def deleteUser(self, userid):
        userid = Util.unifyid(userid)
        if not Util.checkid(userid):
            return False
        # prepare execdata
        return self.connector.dml({
            "type": "delete",
            "schema": config.db_schema,
            "table": config.db_table_users,
            "body": {},
            "predicate": { config.db_table_users_id: userid }
        })

class ProjectMetaStore(MetaStore):
    def createProject(self, userid, projectid):
        projectid = Util.unifyid(projectid)
        # validation
        if not Util.checknumericid(userid):
            raise StandardError("User id is incorrect")
        if not Util.checkid(projectid):
            raise StandardError("Project id is incorrect")
        # create project
        return self.connector.dml({
            "type": "insert",
            "schema": config.db_schema,
            "table": config.db_table_projects,
            "body": {
                config.db_table_projects_userid: userid,
                config.db_table_projects_id: projectid,
                config.db_table_projects_created: datetime.now()
            },
            "predicate": {}
        })

    def getProject(self, userid, projectid):
        projectid = Util.unifyid(projectid)
        # validation
        if not Util.checknumericid(userid) or not Util.checkid(projectid):
            return None
        # everything is ok, return project
        return self.connector.sql({
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
        })

    def deleteProject(self, userid, projectid):
        projectid = Util.unifyid(projectid)
        # validation
        if not Util.checknumericid(userid):
            raise StandardError("User id is incorrect")
        if not Util.checkid(projectid):
            raise StandardError("Project id is incorrect")
        return self.connector.dml({
            "type": "delete",
            "schema": config.db_schema,
            "table": config.db_table_projects,
            "body": {},
            "predicate": {
                config.db_table_projects_userid: userid,
                config.db_table_projects_id: projectid
            }
        })

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
        return self.connector.dml({
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
        })

    def getBranch(self, userid, projectid, branchid):
        branchid = Util.unifyid(branchid)
        # validation
        if not (Util.checknumericid(userid) and Util.checknumericid(projectid)
                and Util.checkid(branchid)):
            return None
        # everything is ok, return branch
        return self.connector.sql({
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
        })

    def getBranchByUniqueId(self, uniquebranchid):
        if not Util.checknumericid(uniquebranchid):
            return None
        # everything is ok, return branch
        return self.connector.sql({
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
        })

    def deleteBranch(self, userid, projectid, branchid):
        branchid = Util.unifyid(branchid)
        # validation
        if not Util.checknumericid(userid):
            raise StandardError("User id is incorrect")
        if not Util.checknumericid(projectid):
            raise StandardError("Project id is incorrect")
        if not Util.checkid(branchid):
            raise StandardError("Branch id is incorrect")
        return self.connector.dml({
            "type": "delete",
            "schema": config.db_schema,
            "table": config.db_table_branches,
            "body": {},
            "predicate": {
                config.db_table_branches_userid: userid,
                config.db_table_branches_projectid: projectid,
                config.db_table_branches_id: branchid
            }
        })

    def deleteBranchByUniqueId(self, uniquebranchid):
        if not Util.checknumericid(uniquebranchid):
            return None
        return self.connector.dml({
            "type": "delete",
            "schema": config.db_schema,
            "table": config.db_table_branches,
            "body": {},
            "predicate": {
                config.db_table_branches_uniqueid: uniquebranchid
            }
        })

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
        # return last row id to know the module id
        return self.connector.dml(execdata, lastrowid=True)

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
                config.db_table_components_uniqueid: None,
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
                config.db_table_components_uniqueid: None,
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
    # better to use within transaction with atomic = False
    def addBranchRevision(self, uniquebranchid, atomic=True):
        if not Util.checknumericid(uniquebranchid):
            raise StandardError("Unique branch id is incorrect")
        # update latest revision as not latest
        self.connector.dml({
            "type": "update",
            "schema": config.db_schema,
            "table": config.db_table_branch_rev,
            "body": {
                config.db_table_branch_rev_latest: 0
            },
            "predicate": {
                config.db_table_branch_rev_branchid: uniquebranchid
            }
        }, atomic=atomic)
        # insert new revision and return last row id
        result = self.connector.dml({
            "type": "insert",
            "schema": config.db_schema,
            "table": config.db_table_branch_rev,
            "body": {
                config.db_table_branch_rev_branchid: uniquebranchid,
                config.db_table_branch_rev_created: datetime.now()
            },
            "predicate": {}
        }, atomic=atomic, lastrowid=True)
        return result

    def getLatestBranchRevision(self, uniquebranchid, atomic=True):
        if not Util.checknumericid(uniquebranchid):
            raise StandardError("Unique branch id is incorrect")
        return self.connector.sql({
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_branch_rev,
            "body": {
                db_table_branch_rev_revisionid: None,
                db_table_branch_rev_branchid: None,
                db_table_branch_rev_created: None,
                db_table_branch_rev_latest: None
            },
            "predicate": {
                config.db_table_branch_rev_branchid: uniquebranchid,
                config.db_table_branch_rev_latest: 1
            }
        }, atomic=atomic)

    def getBranchRevisions(self, uniquebranchid, atomic=True, getsorted=True):
        if not Util.checknumericid(uniquebranchid):
            raise StandardError("Unique branch id is incorrect")
        if getsorted:
            orderby = {
                config.db_table_branch_rev_revisionid: Query.ORDER_BY_ASC
            }
        else:
            orderby = None
        # return result
        return self.connector.sql({
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_branch_rev,
            "body": {
                db_table_branch_rev_revisionid: None,
                db_table_branch_rev_branchid: None,
                db_table_branch_rev_created: None,
                db_table_branch_rev_latest: None
            },
            "predicate": {
                config.db_table_branch_rev_branchid: uniquebranchid
            },
            "orderby": orderby
        }, atomic=atomic, fetchone=False)

    def addModuleRevision(self, moduleid, content, atomic=True):
        if not Util.checknumericid(moduleid):
            raise StandardError("Unique module id is incorrect")
        # update latest revision as not latest
        self.connector.dml({
            "type": "update",
            "schema": config.db_schema,
            "table": config.db_table_module_rev,
            "body": {
                config.db_table_module_rev_latest: 0
            },
            "predicate": {
                config.db_table_module_rev_moduleid: moduleid
            }
        }, atomic=atomic)
        # insert new revision and return last row id
        result = self.connector.dml({
            "type": "insert",
            "schema": config.db_schema,
            "table": config.db_table_module_rev,
            "body": {
                config.db_table_module_rev_moduleid: moduleid,
                config.db_table_module_rev_created: datetime.now(),
                config.db_table_module_rev_content: content
            },
            "predicate": {}
        }, atomic=atomic, lastrowid=True)
        return result

    def getLatestModuleRevision(self, moduleid, atomic=True):
        if not Util.checknumericid(moduleid):
            raise StandardError("Unique module id is incorrect")
        return self.connector.sql({
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_module_rev,
            "body": {
                config.db_table_module_rev_revisionid: None,
                config.db_table_module_rev_moduleid: None,
                config.db_table_module_rev_created: None,
                config.db_table_module_rev_content: None,
                config.db_table_module_rev_latest: None
            },
            "predicate": {
                config.db_table_module_rev_moduleid: moduleid,
                config.db_table_module_rev_latest: 1
            }
        }, atomic=atomic)

    def getModuleRevisions(self, moduleid, atomic=True, getsorted=True):
        if not Util.checknumericid(uniquebranchid):
            raise StandardError("Unique branch id is incorrect")
        if getsorted:
            orderby = { config.db_table_module_rev_revisionid: Query.ORDER_BY_ASC }
        else:
            orderby = None
        # return result
        return self.connector.sql({
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_module_rev,
            "body": {
                config.db_table_module_rev_revisionid: None,
                config.db_table_module_rev_moduleid: None,
                config.db_table_module_rev_created: None,
                config.db_table_module_rev_content: None,
                config.db_table_module_rev_latest: None
            },
            "predicate": {
                config.db_table_module_rev_moduleid: moduleid
            },
            "orderby": orderby
        }, atomic=atomic, fetchone=False)

    def addBranchModuleChain(self, brevid, mrevid, atomic=True):
        if not Util.checknumericid(brevid):
            raise StandardError("Branch revision id is incorrect")
        if not Util.checknumericid(mrevid):
            raise StandardError("Module revision id is incorrect")
        self.connector.dml({
            "type": "insert",
            "schema": config.db_schema,
            "table": config.db_table_branch_module,
            "body": {
                config.db_table_branch_module_brevid: brevid,
                config.db_table_branch_module_mrevid: mrevid
            },
            "predicate": {}
        }, atomic=atomic)

    # returns list (select - fetch all)
    def getBranchModuleChain(self, brevid, atomic=True, getsorted=True):
        if not Util.checknumericid(brevid):
            raise StandardError("Branch revision id is incorrect")
        if getsorted:
            orderby = { config.db_table_branch_module_absorder: Query.ORDER_BY_ASC }
        else:
            orderby = None
        # return result
        return self.connector.sql({
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_branch_module,
            "body": {
                config.db_table_branch_module_brevid: None,
                config.db_table_branch_module_mrevid: None,
                config.db_table_branch_module_absorder: None
            },
            "predicate": {
                config.db_table_branch_module_brevid: brevid
            },
            "orderby": orderby
        }, atomic=atomic, fetchone=False)

    def addComponentRevision(self, componentid, desc, atomic=True):
        if not Util.checknumericid(componentid):
            raise StandardError("Component id is incorrect")
        # update latest revision as not latest
        self.connector.dml({
            "type": "update",
            "schema": config.db_schema,
            "table": config.db_table_component_rev,
            "body": {
                config.db_table_component_rev_latest: 0
            },
            "predicate": {
                config.db_table_component_rev_componentid: componentid
            }
        }, atomic=atomic)
        # insert new revision and return last row id
        return self.connector.dml({
            "type": "insert",
            "schema": config.db_schema,
            "table": config.db_table_component_rev,
            "body": {
                config.db_table_component_rev_componentid: componentid,
                config.db_table_component_rev_description: desc,
                config.db_table_component_rev_created: datetime.now()
            },
            "predicate": {}
        }, atomic=atomic, lastrowid=True)

    def getLatestComponentRevision(self, componentid, atomic=True):
        if not Util.checknumericid(componentid):
            raise StandardError("Unique component id is incorrect")
        return self.connector.sql({
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_component_rev,
            "body": {
                config.db_table_component_rev_revisionid: None,
                config.db_table_component_rev_componentid: None,
                config.db_table_component_rev_description: None,
                config.db_table_component_rev_created: None,
                config.db_table_component_rev_latest: None
            },
            "predicate": {
                config.db_table_component_rev_componentid: componentid,
                config.db_table_component_rev_latest: 1
            }
        }, atomic=atomic)

    def getComponentRevisions(self, componentid, atomic=True, getsorted=True):
        if not Util.checknumericid(componentid):
            raise StandardError("Unique component id is incorrect")
        if getsorted:
            orderby = { config.db_table_component_rev_revisionid: Query.ORDER_BY_ASC }
        else:
            orderby = None
        # return result
        return self.connector.sql({
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_component_rev,
            "body": {
                config.db_table_component_rev_revisionid: None,
                config.db_table_component_rev_componentid: None,
                config.db_table_component_rev_description: None,
                config.db_table_component_rev_created: None,
                config.db_table_component_rev_latest: None
            },
            "predicate": {
                config.db_table_component_rev_componentid: componentid
            },
            "orderby": orderby
        }, atomic=atomic, fetchone=False)
