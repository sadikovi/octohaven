#!/usr/bin/env python

class RedisConst(object):
    REDIS_HOST = ""
    REDIS_PORT = -1
    REDIS_TEST_DB = -1

    @classmethod
    def setRedisSettings(cls, host, port, db):
        print "Settings Redis instance..."
        cls.REDIS_HOST = host
        cls.REDIS_PORT = int(port)
        cls.REDIS_TEST_DB = int(db)
        print "host: %s | port: %d | db: %d" % (cls.REDIS_HOST, cls.REDIS_PORT, cls.REDIS_TEST_DB)

    @classmethod
    def redisHost(cls):
        return cls.REDIS_HOST

    @classmethod
    def redisPort(cls):
        return cls.REDIS_PORT

    @classmethod
    def redisTestDb(cls):
        return cls.REDIS_TEST_DB
