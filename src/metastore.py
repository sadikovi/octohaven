#!/usr/bin/env python
import src.config as config
from datetime import datetime

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
        if not name or name == "": raise StandardError("User name is incorrect")
        if not created: created = datetime.now()
        if self.getUser({"name": name}): raise StandardError("User name is taken")
        # prepare exec data
        execdata = {
            "schema": config.db_schema,
            "table": config.db_table_users,
            "data": {
                config.db_table_users_name: name,
                config.db_table_users_created: created,
                confg.db_table_users_deleted: 0
            }
        }
        return self.connector.insert(execdata)

    # get user
    def getUser(self, data):
        name = data[config.db_table_users_name]
        if name:
            execdata = {
                "type": "select",
                "schema": config.db_schema,
                "table": config.db_table_users,
                "data": {
                    config.db_table_users_name: name
                },
                "assets": [
                    config.db_table_users_name,
                    config.db_table_users_created,
                    config.db_table_users_deleted
                ]
            }
            return self.connector.select(execdata)
        return None

    # delete user
    def deleteUser(self, data):
        name = data[config.db_table_users_name]
        if not name: raise StandardError("User name is undefined")
        execdata = {
            "schema": config.db_schema,
            "table": config.db_table_users,
            "data": {
                config.db_table_users_name: name,
                config.db_table_users_deleted: 1
            }
        }
        return self.connector.update(execdata)

    # create new project
    def createProject(self, data):
        pass

    # get project
    def getProject(self, data):
        pass

    def deleteProject(self, data):
        pass
