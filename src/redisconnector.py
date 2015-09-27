#!/usr/bin/env python

import redis
import cPickle
from types import DictType, ListType

class RedisConnectionPool(redis.ConnectionPool):
    def __init__(self, settings):
        self._host = settings["host"] if "host" in settings else None
        self._port = settings["port"] if "port" in settings else None
        self._db = settings["db"] if "db" in settings else None

        if self._host is None or self._port is None or self._db is None:
            raise StandardError("Connection pool requires host, port and db to be set")

        super(RedisConnectionPool, self).__init__(
            host=self._host,
            port=self._port,
            db=self._db
        )

class RedisConnector(object):
    def __init__(self, pool):
        if type(pool) is not RedisConnectionPool:
            raise StandardError("Connection pool must be RedisConnectionPool")
        # create redis instance
        self._pool = pool
        self._redis = redis.Redis(connection_pool=self._pool)
        self._prefix = ":redis:"

    def getPool(self):
        return self._pool

    def _key(self, key):
        # key is always lowercase
        return ("%s%s"%(self._prefix, key)).lower()

    # object serialization using cPickle
    def serialize(self, obj):
        try:
            return cPickle.dumps(obj)
        except:
            raise StandardError("Pickling object [%s: type %s] failed" %(obj, type(obj)))

    # object deserialization using cPickle
    def deserialize(self, info):
        try:
            return cPickle.loads(info)
        except:
            raise StandardError("Unpickling info [%s] failed" %(info))

    # stores object for key
    def store(self, key, obj):
        info = self.serialize(obj)
        pipe = self._redis.pipeline()
        pipe.set(self._key(key), info).execute()

    # returns object for key; if no key found, returns None
    def get(self, key):
        fullkey, obj = self._key(key), None
        if self._redis.exists(fullkey):
            info = self._redis.get(fullkey)
            obj = self.deserialize(info)
        return obj

    def storeCollection(self, key, args):
        if type(args) is not ListType:
            raise StandardError("Expected ListType, got %s" + type(args))
        pipe = self._redis.pipeline()
        for arg in args:
            pipe.sadd(self._key(key), self.serialize(arg))
        pipe.execute()

    def getCollection(self, key):
        # return as list, not set
        fullkey = self._key(key)
        if not self._redis.exists(fullkey):
            return None
        members = self._redis.smembers(fullkey)
        return list([self.deserialize(x) for x in members])

    def delete(self, key):
        key = self._key(key)
        self._redis.delete(key)

    def flushdb(self):
        self._redis.flushdb()

    def removeFromCollection(self, key, args):
        fullkey = self._key(key)
        pipe = self._redis.pipeline()
        for arg in args:
            pipe.srem(fullkey, self.serialize(arg))
        pipe.execute()
