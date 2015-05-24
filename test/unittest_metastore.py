#!/usr/bin/env python

import unittest
from datetime import datetime
import src.mysql.config as config
from src.mysql.metastore import Util, MetaStore, UserMetaStore, ProjectMetaStore
from src.mysql.metastore import BranchMetaStore, ModuleMetaStore, ComponentMetaStore
from src.connector.mysqlconnector import MySqlConnector
from types import DictType, IntType
import uuid
from mysql.connector import IntegrityError

class Util_TS(unittest.TestCase):
    def test_checkid(self):
        self.assertEqual(Util.checkid(None), False)
        self.assertEqual(Util.checkid({}), False)
        self.assertEqual(Util.checkid([]), False)
        self.assertEqual(Util.checkid(12345), False)
        self.assertEqual(Util.checkid("someid"), True)

    def test_checknumericid(self):
        self.assertEqual(Util.checknumericid(None), False)
        self.assertEqual(Util.checknumericid({}), False)
        self.assertEqual(Util.checknumericid([]), False)
        self.assertEqual(Util.checknumericid("someid"), False)
        self.assertEqual(Util.checknumericid(12345), True)

class StoreTestCase(unittest.TestCase):
    def setUp(self):
        settings = {
            "host": config.mysql_host,
            "user": config.mysql_user,
            "pass": config.mysql_pass,
            "schema": config.db_schema
        }
        self.connector = MySqlConnector(settings)
        prefix = uuid.uuid4().hex
        self.userid = prefix + "-test-user"
        self.userpass = prefix + "-test-pass"
        self.projectid = prefix + "-test-project"
        self.branchid = prefix + "-test-branch"
        self.componentid = prefix + "-test-component"
        self.clearData()

    def tearDown(self):
        self.clearData()
        self.connector.disconnect()
        self.connector = None

    def clearData(self):
        # clear user
        self.connector.dml({
            "type": "delete",
            "schema": config.db_schema, "table": config.db_table_users,
            "body": {},
            "predicate": { config.db_table_users_id: self.userid }
        })
        # clear project
        self.connector.dml({
            "type": "delete",
            "schema": config.db_schema, "table": config.db_table_projects,
            "body": {},
            "predicate": { config.db_table_projects_id: self.projectid }
        })
        # clear branch
        self.connector.dml({
            "type": "delete",
            "schema": config.db_schema, "table": config.db_table_branches,
            "body": {},
            "predicate": { config.db_table_branches_id: self.branchid }
        })
        # clear component
        self.connector.dml({
            "type": "delete",
            "schema": config.db_schema, "table": config.db_table_components,
            "body": {},
            "predicate": { config.db_table_components_id: self.componentid }
        })

class MetaStore_TS(StoreTestCase):
    def test_metastore(self):
        with self.assertRaises(StandardError):
            MetaStore(None)
        store = MetaStore(self.connector)

class UserMetaStore_TS(StoreTestCase):
    def test_usermetastore(self):
        with self.assertRaises(StandardError):
            UserMetaStore(None)
        store = UserMetaStore(self.connector)
        # create user
        res = store.createUser(self.userid, self.userpass)
        self.assertEqual(res, True)
        # get user
        user = store.getUser(self.userid)
        self.assertEqual(type(user), DictType)
        self.assertEqual(user[unicode(config.db_table_users_id)], self.userid)
        self.assertEqual(user[unicode(config.db_table_users_pass)], self.userpass)
        # check that user exists
        self.assertEqual(store.userExists(self.userid), True)
        # create the same user again - raise exception
        with self.assertRaises(StandardError):
            store.createUser(self.userid)
        # delete user
        res = store.deleteUser(self.userid)
        self.assertEqual(res, True)
        # get user - None should be returned
        user = store.getUser(self.userid)
        self.assertEqual(user, None)

class ProjectMetaStore_TS(StoreTestCase):
    def test_projectmetastore(self):
        unique_userid = 99999999
        with self.assertRaises(StandardError):
            ProjectMetaStore(None)
        store = ProjectMetaStore(self.connector)
        # create project
        res = store.createProject(unique_userid, self.projectid)
        self.assertEqual(res, True)
        # create project again
        with self.assertRaises(IntegrityError):
            res = store.createProject(unique_userid, self.projectid)
        # get project
        project = store.getProject(unique_userid, self.projectid)
        self.assertEqual(type(project), DictType)
        self.assertEqual(project[unicode(config.db_table_projects_id)], self.projectid)
        # delete project
        res = store.deleteProject(unique_userid, self.projectid)
        # check that nothing returns
        project = store.getProject(unique_userid, self.projectid)
        self.assertEqual(project, None)

class BranchMetaStore_TS(StoreTestCase):
    def test_branchmetastore(self):
        unique_userid = 99999999
        unique_projectid = 99999999
        with self.assertRaises(StandardError):
            BranchMetaStore(None)
        store = BranchMetaStore(self.connector)
        # create branch
        res = store.createBranch(unique_userid, unique_projectid, self.branchid)
        self.assertEqual(res, True)
        # get branch
        branch = store.getBranch(unique_userid, unique_projectid, self.branchid)
        self.assertEqual(type(branch), DictType)
        self.assertEqual(branch[unicode(config.db_table_branches_id)], self.branchid)
        # get branch by unique id
        unique_branchid = branch[unicode(config.db_table_branches_uniqueid)]
        branch_u = store.getBranchByUniqueId(unique_branchid)
        self.assertEqual(branch_u, branch)
        # delete branch
        res = store.deleteBranch(unique_userid, unique_projectid, self.branchid)
        self.assertEqual(res, True)
        self.assertEqual(store.getBranchByUniqueId(unique_branchid), None)
        # still call another method to check syntax
        store.deleteBranchByUniqueId(unique_branchid)

class ModuleMetaStore_TS(StoreTestCase):
    def test_modulemetastore(self):
        with self.assertRaises(StandardError):
            ModuleMetaStore(None)
        store = ModuleMetaStore(self.connector)
        # create module
        moduleid = store.createModule()
        self.assertEqual(type(moduleid), IntType)
        self.assertTrue(moduleid > 0)
        # get module
        module = store.getModule(moduleid)
        self.assertEqual(type(module), DictType)

class ComponentMetaStore_TS(StoreTestCase):
    def test_componentmetastore(self):
        with self.assertRaises(StandardError):
            ComponentMetaStore(None)
        store = ComponentMetaStore(self.connector)
        # create component
        unique_userid = 99999999
        ctype, fileurl = "test-type", "test-fileurl"
        res = store.createComponent(unique_userid, self.componentid, ctype, fileurl)
        self.assertEqual(res, True)
        # get component
        component = store.getComponent(unique_userid, self.componentid, ctype)
        self.assertEqual(type(component), DictType)
        self.assertEqual(component[unicode(config.db_table_components_id)], self.componentid)
        # get component by unique id
        unique_componentid = component[unicode(config.db_table_components_uniqueid)]
        component_u = store.getComponentByUniqueId(unique_componentid)
        self.assertEqual(component_u, component)
        # delete component
        res = store.deleteComponent(unique_userid, self.componentid, ctype)
        self.assertEqual(res, True)
        self.assertEqual(store.getComponentByUniqueId(unique_componentid), None)
        # delete component by unique id
        # just call method to check syntax
        store.deleteComponentByUniqueId(unique_componentid)

# Load test suites
def _suites():
    return [
        Util_TS,
        MetaStore_TS,
        UserMetaStore_TS,
        ProjectMetaStore_TS,
        BranchMetaStore_TS,
        ModuleMetaStore_TS,
        ComponentMetaStore_TS
    ]

# Load tests
def loadSuites():
    # global test suite for this module
    gsuite = unittest.TestSuite()
    for suite in _suites():
        gsuite.addTest(unittest.TestLoader().loadTestsFromTestCase(suite))
    return gsuite

if __name__ == '__main__':
    suite = loadSuites()
    print ""
    print "### Running tests ###"
    print "-" * 70
    unittest.TextTestRunner(verbosity=2).run(suite)
