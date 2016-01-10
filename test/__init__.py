#!/usr/bin/env python

import urllib2

# Shared settings
class Settings(object):
    _map = None

    def __init__(self):
        self.settings = {}

    def set(self, key, value):
        self.settings[key] = value

    def get(self, key):
        return self.settings[key] if key in self.settings else None

    @classmethod
    def mp(cls):
        if not cls._map:
            cls._map = Settings()
        return cls._map

# helper to send request
class Request(object):
    @staticmethod
    def post(url, data):
        return urllib2.urlopen(url, data).read()

    @staticmethod
    def get(url):
        return urllib2.urlopen(url).read()
