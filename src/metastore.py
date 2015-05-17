#!/usr/bin/env python

import src.config as config
from datetime import datetime
from types import StringType

class Metastore(object):
    def __init__(self, config):
        if not config:
            raise StandardError("Config is undefined")
        if not config.connector:
            raise StandardError("Connector is undefined")
        self.connector = config.connector

    # create new User
    def createUser(self, data):
        name = data[config.db_table_users_name]
        created = data[config.db_table_users_created]
        # validate fields
        if not name or name == "":
            raise StandardError("User name is incorrect")
        name = name.strip()
        created = datetime.now() if not created else created
        if self.userExists(name):
            raise StandardError("User name is taken")
        # prepare exec data
        execdata = {
            "type": "insert",
            "schema": config.db_schema,
            "table": config.db_table_users,
            "body": {},
            "predicate": {
                config.db_table_users_name: name.strip(),
                config.db_table_users_created: created,
                confg.db_table_users_deleted: 0
            }
        }
        return self.connector.dml(execdata)

    # get user
    def getUser(self, name, checkexistsonly=False):
        name = name.strip() if name and type(name) is StringType else None
        if not name:
            return None

        if checkexistsonly:
            body = {config.db_table_users_name: None}
        else:
            body = {
                config.db_table_users_name: None,
                config.db_table_users_created: None,
                config.db_table_users_deleted: None
            }
        # prepare execdata
        execdata = {
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_users,
            "body": body
            "predicate": {
                config.db_table_users_name: name
            }
        }
        return self.connector.sql(execdata)

    # check if user exists
    def userExists(self, name):
        return True and self.getUser(name, True)

    # delete user
    def deleteUser(self, name):
        name = name.strip() if name and type(name) is StringType else None
        if not name:
            raise StandardError("User name is undefined")
        # prepare execdata
        execdata = {
            "type": "update"
            "schema": config.db_schema,
            "table": config.db_table_users,
            "body": {
                config.db_table_users_deleted: 1
            },
            "predicate": {
                config.db_table_users_name: name
            }
        }
        return self.connector.dml(execdata)

    # create new project
    def createProject(self, name, ownerid):
        # create project
        execdata = {
            "type": "insert",
            "schema": config.db_schema,
            "table": config.db_table_projects,
            "body": {},
            "predicate": {
                config.db_table_projects_name: name,
                config.db_table_projects_created: datetime.now(),
                config.db_table_projects_owner: ownerid,
                config.db_table_projects_deleted: 0
            }
        }
        projectid = self.connector.dml(execdata, lastrowid=True)
        # get project
        branchid = self.createMasterBranch(projectid)
        # create branch
        self.updateMainBranch(projectid, branchid)
        return projectid

    # get project
    def getProject(self, id):
        if not id:
            return None
        execdata = {
            "type": "select",
            "schema": config.db_schema,
            "table": config.db_table_projects,
            "body": {
                config.db_table_projects_id: None,
                config.db_table_projects_name: None,
                config.db_table_projects_created: None,
                config.db_table_projects_branch: None,
                config.db_table_projects_owner: None,
                config.db_table_projects_deleted: None
            },
            "predicate": {
                config.db_table_projects_id: id
            }
        }
        return self.connector.sql(execdata)

    def deleteProject(self, id):
        if not id:
            raise StandardError("Project id is undefined")
        execdata = {
            "type": "update",
            "schema": config.db_schema,
            "table": config.db_table_projects,
            "body": {
                config.db_table_projects_deleted: 1
            },
            "predicate": {
                config.db_table_projects_id: id
            }
        }
        return self.connector.dml(execdata)

    def createMasterBranch(self, projectid):
        pass

    def updateMainBranch(self, projectid, branchid):
        pass
