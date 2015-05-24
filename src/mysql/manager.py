#!/usr/bin/env python

import src.mysql.config as config
from src.connector.mysqlconnector import MySqlConnector
from src.mysql.core import User
from src.mysql.metastore import UserMetaStore

class Manager(object):
    # default nice layer on top of Metastore
    def __init__(self, connector):
        if type(connector) is not MySqlConnector:
            raise StandardError("Connector type is required, passed %s" %(type(connector)))
        self.connector = connector

class UserManager(Manager):
    def __init__(self, connector):
        super(UserManager, self).__init__(connector)
        # build user metastore to handle user operations
        self.usermetastore = UserMetaStore(self.connector)

    def getUser(self, userid):
        obj = self.usermetastore.getUser(userid)
        if obj:
            uniqueid_key = unicode(config.db_table_users_uniqueid)
            id_key = unicode(config.db_table_users_id)
            created_key = unicode(config.db_table_users_created)
            uniqueid, id, created = obj[uniqueid_key], obj[id_key], obj[created_key]
            # create and return User object
            return User(uniqueid, id, created)
        else:
            return None

    def getProjects(self, user):
        pass
