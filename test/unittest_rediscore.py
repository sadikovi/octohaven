#!/usr/bin/env python

import unittest
from src.redis.core import User, Project
from src.redis.errors import CoreError
from types import StringType, DictType, ListType
import time

class RedisCore_TS(unittest.TestCase):
    def test_user(self):
        values = [
            (True, "123", "name 1", "email 1", time.time()),
            (True, "123", 1, "1", time.time()),
            (True, "123", "name 1", 1, time.time()),
            (False, "123", "name 1", "1", None),
        ]
        for st, eid, name, email, created in values:
            if st:
                user = User(eid, name, email, created)
                # check properties
                self.assertEqual(user._id, str(eid))
                self.assertEqual(user._name, str(name))
                self.assertEqual(user._email, str(email))
                self.assertEqual(user._created, created)
            else:
                with self.assertRaises(CoreError):
                    User(eid, name, email, created)

    def test_user_create(self):
        _id, _name, _email = "testid", "testname", "testemail"
        # create user
        user = User(_id, _name, _email)
        settings = user.dict()
        self.assertEqual(type(settings), DictType)
        # create user from class
        newuser = User.create(settings)
        self.assertEqual(newuser._id, user._id)
        self.assertEqual(newuser._name, user._name)
        self.assertEqual(newuser._email, user._email)
        self.assertEqual(newuser._created, user._created)
        # delete key
        del settings["_name"]
        with self.assertRaises(KeyError):
            User.create(settings)

    def test_project_failures(self):
        ids = [
            (True, "1"),
            (True, "12"),
            (False, "123"),
            (True, "1$5@34"),
            (False, "sdfljsdf-sdfl-123-sdf")
        ]
        name, userid, created = "name", None, time.time()
        for fl, _id in ids:
            if fl:
                with self.assertRaises(CoreError):
                    Project(_id, name, userid, created)
            else:
                project = Project(_id, name, userid, created)
                self.assertEqual(type(project), Project)
                self.assertEqual(project._id, _id)

    def test_project(self):
        values = [
            (True, "123", "name 1", "userid 1", time.time()),
            (True, "123", 1, "userid 1", time.time()),
            (True, "123", "name 1", 1, time.time()),
            (True, "123", "name 1", None, time.time()),
            (False, "123", "name 1", "userid 1", None),
        ]
        for st, eid, name, userid, created in values:
            if st:
                project = Project(eid, name, userid, created)
                # check properties
                self.assertEqual(project._id, str(eid))
                self.assertEqual(project._name, str(name))
                self.assertEqual(project._userid, str(userid) if userid else None)
                self.assertEqual(project._created, created)
            else:
                with self.assertRaises(CoreError):
                    Project(eid, name, userid, created)

    def test_project_create(self):
        # create project
        _id, _name, _userid = "testid", "testname", None
        project = Project(_id, _name, _userid)
        settings = project.dict()
        self.assertEqual(type(settings), DictType)
        # create project from class
        newproject = Project.create(settings)
        self.assertEqual(type(newproject), Project)
        self.assertEqual(newproject._id, project._id)
        self.assertEqual(newproject._name, project._name)
        self.assertEqual(newproject._userid, project._userid)
        self.assertEqual(newproject._created, project._created)
        # delete key
        del settings["_id"]
        with self.assertRaises(KeyError):
            Project.create(settings)

# Load test suites
def _suites():
    return [
        RedisCore_TS
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
