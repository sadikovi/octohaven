#!/usr/bin/env python

# private decorator
def private(f):
    # This function is what we "replace" hello with
    def wrapper(*args, **kw):
        return f(*args, **kw)
    return wrapper
