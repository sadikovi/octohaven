#!/usr/bin/env python

import unittest
from src.redis.core import User, Project
from src.redis.errors import CoreError
from types import StringType, DictType, ListType
import time

class RedisCore_TS(unittest.TestCase):
    def test_user(self):
        values = [
            (True, "1", "name 1", "email 1", time.time()),
            (True, "1", 1, "1", time.time()),
            (True, "1", "name 1", 1, time.time()),
            (False, "1", "name 1", "1", None),
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

    def test_project(self):
        values = [
            (True, "1", "name 1", "userid 1", time.time()),
            (True, "1", 1, "userid 1", time.time()),
            (True, "1", "name 1", 1, time.time()),
            (True, "1", "name 1", None, time.time()),
            (False, "1", "name 1", "userid 1", None),
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
