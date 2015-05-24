#!/usr/bin/env python

import redis
from src.redis.errors import ConnectorError
from types import DictType, IntType, FloatType, StringType, BooleanType, NoneType

class RedisConnectionPool(object):
    def __init__(self, settings):
        self._settings = settings
        self._pool = redis.ConnectionPool(
            host=settings["host"],
            port=settings["port"],
            db=settings["db"]
        )

class RedisConnector(object):
    def __init__(self, poolhandler):
        if type(poolhandler) is not RedisConnectionPool:
            raise ConnectorError("Connection pool is wrong")
        # create redis instance
        self._redis = redis.Redis(connection_pool=poolhandler._pool)
        # apply prefix for each key
        self._settings = poolhandler._settings
        self._prefix = "%s:" %(self._settings["prefix"] if "prefix" in self._settings else "redis")

    def _compressValue(self, value):
        hashtype = "%s"%(type(value))
        hashvalue = ""
        if type(value) is BooleanType:
            hashvalue = "1" if value else "0"
        else:
            hashvalue = "%s"%(value)
        return (hashtype, hashvalue)

    def _decompressValue(self, hashtype, hashvalue):
        value = ""
        if hashtype == "%s"%(NoneType):
            value = None
        elif hashtype == "%s"%(IntType):
            value = int(hashvalue)
        elif hashtype == "%s"%(FloatType):
            value = float(hashvalue)
        elif hashtype == "%s"%(BooleanType):
            value = True if hashvalue == "1" else False
        else:
            value = str(hashvalue)
        return value

    def _key(self, key):
        return "%s-%s"%(self._prefix, key)

    def storeObject(self, key, object={}):
        # handle int, float, str, bool, None
        if type(object) is not DictType:
            raise ConnectorError("Object is not a DictType")
        # append prefix
        key = self._key(key)
        # process object
        info, idseq = {}, 0
        for k, v in object.items():
            hashkey = "[%s#hashkey]"%(idseq)
            hashtype, hashvalue = self._compressValue(v)
            info[k] = hashkey
            info["%s:TYPE"%(hashkey)] = hashtype
            info["%s:VALUE"%(hashkey)] = hashvalue
            idseq += 1
        pipe = self._redis.pipeline()
        pipe.hmset(key, info).execute()

    def getObject(self, key):
        key, object = self._key(key), {}
        if self._redis.exists(key):
            # parse object
            info = self._redis.hgetall(key)
            for k, v in info.items():
                hashkey = v
                typekey = "%s:TYPE"%(hashkey)
                valuekey = "%s:VALUE"%(hashkey)
                if typekey in info and valuekey in info:
                    object[k] = self._decompressValue(info[typekey], info[valuekey])
            return object
        else:
            return None

    def storeConnection(self, key, *args):
        key = self._key(key)
        pipe = self._redis.pipeline()
        for arg in args:
            pipe.sadd(key, arg)
        pipe.execute()

    def getConnection(self, key, aslist=True):
        # return as list, not set
        key = self._key(key)
        if self._redis.exists(key):
            members = self._redis.smembers(key)
            if aslist:
                members = list(members)
            return members
        else:
            return None

    def delete(self, key):
        self._redis.delete(key)

    def flushdb(self):
        self._redis.flushdb()
