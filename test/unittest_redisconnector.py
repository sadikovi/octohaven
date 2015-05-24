#!/usr/bin/env python

import unittest
import src.redis.config as config
from src.connector.redisconnector import RedisConnectionPool, RedisConnector
from types import StringType, DictType, ListType


test_pool = RedisConnectionPool(config.test_settings)

class RedisConnector_TS(unittest.TestCase):
    def setUp(self):
        self._redis = RedisConnector(test_pool)
        self._redis.flushdb()

    def tearDown(self):
        self._redis = None

    def test_compressValue(self):
        values = [None, "str", 1, 1.2, {}, []]
        for value in values:
            hashtype, hashvalue = self._redis._compressValue(value)
            self.assertEqual(hashtype, "%s"%(type(value)))
            self.assertEqual(type(hashvalue), StringType)

    def test_decompressValue(self):
        values = [None, "str", 1, 1.2, False, True, {}, []]
        for value in values:
            hashtype, hashvalue = self._redis._compressValue(value)
            res = self._redis._decompressValue(hashtype, hashvalue)
            if type(value) in [DictType, ListType]:
                self.assertEqual(res, str(value))
            else:
                self.assertEqual(res, value)

    def test_key(self):
        values = [None, "str", 1, 1.2, {}, []]
        for value in values:
            pseudokey = self._redis._key(value)
            self.assertEqual(type(pseudokey), StringType)
            self.assertEqual(
                pseudokey.split("-")[0],
                self._redis._prefix
            )

    def test_storeAndGetObject(self):
        _key = "test#storeobject"
        # test object
        info = {
            "string": "str",
            "int": 123,
            "negint": -123,
            "float": 0.2234,
            "bool": False,
            "posbool": True,
            "none": None,
            "dict": {"a":1, "b":2},
            "list": [1, 2, 3]
        }
        # store object
        self._redis.storeObject(_key, info)
        object = self._redis.getObject(_key)
        self.assertEqual(sorted(object.keys()), sorted(info.keys()))
        for key in object.keys():
            if type(info[key]) in [DictType, ListType]:
                self.assertEqual(object[key], str(info[key]))
            else:
                self.assertEqual(object[key], info[key])

    def test_storeConnection(self):
        _key = "test#storeconnection"
        args = ["a", "b", "c", "d", "e", "a", "b"]
        for arg in args:
            self._redis.storeConnection(_key, arg)
        # get connections
        res = self._redis.getConnection(_key, aslist=False)
        self.assertEqual(res, set(args))
        res = self._redis.getConnection(_key, aslist=True)
        self.assertEqual(res, list(set(args)))


# Load test suites
def _suites():
    return [
        RedisConnector_TS
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
