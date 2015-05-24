#!/usr/bin/env python

import unittest
from src.redis.core import User, Project
import src.redis.config as config
from src.connector.redisconnector import RedisConnectionPool, RedisConnector
from src.redis.manager import Manager
from src.redis.errors import CoreError
from types import FloatType, ListType

test_pool = RedisConnectionPool(config.test_settings)

class RedisManager_TS(unittest.TestCase):
    def setUp(self):
        self._redis = RedisConnector(test_pool)
        self._redis.flushdb()
        self._manager = Manager(self._redis)

    def tearDown(self):
        self._manager = None
        self._redis = None

    def test_user(self):
        print ""
        eid, name, email = "test_user", "test_name", "test_email"
        # get user
        user = self._manager.getUser(eid)
        self.assertEqual(user, None)
        print ":GET user [no exist] - OK"
        # create user
        user = self._manager.createUser(eid, name, email)
        self.assertEqual(type(user), User)
        self.assertEqual(user._id, eid)
        self.assertEqual(user._name, name)
        self.assertEqual(user._email, email)
        self.assertEqual(type(user._created), FloatType)
        print ":CREATE user [] - OK"
        # retrieve user
        backuser = self._manager.getUser(eid)
        self.assertEqual(type(backuser), User)
        self.assertEqual(backuser._id, user._id)
        self.assertEqual(backuser._name, user._name)
        self.assertEqual(backuser._email, user._email)
        self.assertEqual(round(backuser._created, 2), round(user._created, 2))
        print ":GET user [exist] - OK"

    def test_project(self):
        print ""
        pid, name, uid = "test_id", "test_name", None
        # get project
        project = self._manager.getProject(uid, pid)
        self.assertEqual(project, None)
        print ":GET project [no exist] - OK"
        # create project
        project = self._manager.createProject(uid, pid, name)
        self.assertEqual(type(project), Project)
        self.assertEqual(project._id, pid)
        self.assertEqual(project._name, name)
        self.assertEqual(project._userid, uid)
        self.assertEqual(type(project._created), FloatType)
        print ":CREATE project [] - OK"
        # get project
        backproj = self._manager.getProject(uid, pid)
        self.assertEqual(type(backproj), Project)
        self.assertEqual(backproj._id, project._id)
        self.assertEqual(backproj._name, project._name)
        self.assertEqual(backproj._userid, project._userid)
        self.assertEqual(round(backproj._created, 2), round(project._created, 2))
        print ":GET project [exist] - OK"

    def test_projectUserConn(self):
        print ""
        uid = "test_user"
        pids = ["project1", "project2", "project3"]
        # get connections
        res = self._manager.projectsForUser(uid, asobject=True)
        self.assertEqual(res, None)
        print ":GET project-user connection [no exist] - OK"
        # add connections
        for pid in pids:
            project = self._manager.createProject(uid, pid, "test_project")
            self._manager.addProjectForUser(uid, pid)
        print ":ADD project-user connection [] - OK"
        # get connections again
        res = self._manager.projectsForUser(uid, asobject=False)
        self.assertEqual(type(res), ListType)
        self.assertEqual(sorted(res), sorted(pids))
        print ":GET project-user connection [as str] - OK"
        # get connections as objects
        res = self._manager.projectsForUser(uid, asobject=True)
        self.assertEqual(type(res), ListType)
        for obj in res:
            self.assertEqual(type(obj), Project)
        print ":GET project-user connection [as obj] - OK"

# Load test suites
def _suites():
    return [
        RedisManager_TS
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
