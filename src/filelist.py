#!/usr/bin/env python

import os
from types import ListType

class File(object):
    def __init__(self, status, path, rank):
        ok = os.path.isabs(path)
        if not ok:
            raise StandardError("Path " + path + " is not absolute")
        self.status = status
        self.path = path
        self.rank = rank

    def toDict(self):
        return {"status": self.status, "path": self.path, "rank": self.rank}

class JarFile(File):
    def __init__(self, path):
        super(JarFile, self).__init__("JAR", path, 2)

class Directory(File):
    def __init__(self, path):
        super(Directory, self).__init__("DIR", path, 1)

class FileList(object):
    @classmethod
    def discover(cls, root):
        if not isinstance(root, Directory):
            raise StandardError("Expected File instance, got " + type(root))
        files = []
        for entry in os.listdir(root.path):
            path = os.path.join(root.path, entry)
            if os.path.isdir(path):
                files.append(Directory(path))
            elif path.lower().endswith(".jar"):
                files.append(JarFile(path))
        return files

    @classmethod
    def sortFiles(cls, files):
        if type(files) is not ListType:
            raise StandardError("Expected ListType, got " + str(type(files)))
        # sort function by rank and path name
        def compare(x, y):
            delta = x.rank - y.rank
            return cmp(x.path, y.path) if delta == 0 else delta
        return sorted(files, compare)

    @classmethod
    def listAsDict(cls, files):
        if type(files) is not ListType:
            raise StandardError("Expected ListType, got " + str(type(files)))
        return [x.toDict() for x in files]
