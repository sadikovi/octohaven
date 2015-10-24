#!/usr/bin/env python

from types import DictType
from redisconnector import RedisConnector
from utils import *

# Storage manager is generic layer on top of connector, abstracts interactions with a storage.
# Has some general methods to operate with collections as well as retrieving objects.
class StorageManager(object):
    def __init__(self, connector):
        if type(connector) is not RedisConnector:
            raise StandardError("Connector type " + str(type(connector)) + "is not supported")
        self.connector = connector

    # returns instance of class "klass", and requires to have method `::fromDict()`
    # if cls is empty then returns just received object
    def itemForUid(self, uid, klass=None):
        obj = self.connector.get(uid)
        if not obj:
            return None
        return klass.fromDict(obj) if klass else obj

    # retrieving items for a particular keyspace with limit and sorting
    # - keyspace => keyspace to fetch, e.g. job status like CREATED, WAITING
    # - limit => limit results by the number provided, if limit is less than 0, return all results
    # - cmpFunc => comparison function, see Python documentation for details
    # - klass => class to apply convertion to and from, if None operates with objects, otherwise
    # must support methods `::toDict()` and `::fromDict()`
    def itemsForKeyspace(self, keyspace, limit=30, cmpFunc=None, klass=None):
        doLimit = limit >= 0
        doSort = cmp is not None
        # fetch all uids for that keyspace
        uids = self.connector.getCollection(keyspace)
        items = [self.itemForUid(uid, klass) for uid in uids] if uids else []
        # filter out items that are None, e.g. this can happen when job is registered, but it is
        # not saved. This is a rare case, but we should filter them in order to avoid confusion
        items = [item for item in items if item is not None]
        # perform sorting using cmp
        items = sorted(items, cmp=cmpFunc) if doSort else items
        # limit results if possible
        items = items[:limit] if doLimit else items
        return items

    def saveItem(self, item, klass=None):
        if type(item) is not klass and type(item) is not DictType:
            raise StandardError("Unrecognized type for item, found: " + str(type(item)))
        uid = item.uid if klass else item["uid"]
        obj = item.toDict() if klass else item
        self.connector.store(uid, obj)

    def addItemToKeyspace(self, keyspace, uid):
        self.connector.storeCollection(keyspace, [uid])

    def removeItemFromKeyspace(self, keyspace, uid):
        self.connector.removeFromCollection(keyspace, [uid])
