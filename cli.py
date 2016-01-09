#!/usr/bin/env python

from types import ListType

# Assumes that CLI arguments are specified in format "key = value"
class CLI(object):
    def __init__(self, args, strict=False):
        if type(args) is not ListType:
            raise StandardError("Expected arguments of ListType, got %s" % str(type(args)))
        self.params = dict(self.pairs(args, strict))

    def pairs(self, args, strict=False):
        opts = []
        for arg in args:
            pair = arg.split("=", 1)
            if len(pair) != 2:
                msg = "Parameter '%s' cannot be parsed" % arg
                if strict:
                    raise StandardError(msg)
                else:
                    print "[WARN] %s" % msg
            else:
                key, value = pair
                opts.append((key.strip(), value.strip()))
        return opts

    def getOrElse(self, key, default):
        return self.params[key] if key in self.params else default

    # get method with default None
    def get(self, key):
        return self.getOrElse(key, None)
