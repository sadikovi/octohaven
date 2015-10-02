#!/usr/bin/env python

import unittest
from src.redisconnector import RedisConnectionPool, RedisConnector
from types import StringType, DictType, ListType

class RedisConnectorTestSuite(unittest.TestCase):
    def setUp(self):
        self._test_pool = RedisConnectionPool({
            "host": "localhost",
            "port": 6379,
            "db": 11
        })
        self._redis = RedisConnector(self._test_pool)
        self._redis.flushdb()

    def tearDown(self):
        self._redis = None

    def test_key(self):
        key = "test"
        fullkey = self._redis._key(key)
        self.assertEqual(fullkey, self._redis._prefix + key)

    def test_serializeAndDeserialize(self):
        obj = {"name": "A", "checked": True, "number": 12}
        info = self._redis.serialize(obj)
        res = self._redis.deserialize(info)
        self.assertEqual(res, obj)

    def test_handleObject(self):
        obj = {"name": "A", "checked": True, "number": 12}
        self._redis.store("obj", obj)
        res = self._redis.get("obj")
        self.assertEqual(res, obj)

    def test_handleCollection(self):
        arr = ["a", "b", "c", "d"]
        self._redis.storeCollection("col", arr)
        res = self._redis.getCollection("col")
        self.assertEqual(sorted(res), sorted(arr))

    def test_delete(self):
        self._redis.store("obj", {"name": "Cooper", "checked": True})
        self._redis.delete("obj")
        res = self._redis.get("obj")
        self.assertEqual(res, None)

    def test_removeFromCollection(self):
        arr = ["a", "b", "c", "d"]
        self._redis.storeCollection("col", arr)
        self._redis.removeFromCollection("col", ["a", "c"])
        res = self._redis.getCollection("col")
        self.assertEqual(sorted(res), sorted(["b", "d"]))


# Load test suites
def _suites():
    return [
        RedisConnectorTestSuite
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
