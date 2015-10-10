#!/usr/bin/env python

import os, re
from utils import *

class File(object):
    # name is a file's name
    # path is a path relative to some root
    # tp is a type of a file (DIR, JAR, etc.)
    # rank is a sorting rank
    def __init__(self, name, path, tp, rank):
        self.name = name
        self.path = path
        self.tp = tp
        self.rank = rank

    def toDict(self):
        return {"name": self.name, "path": self.path, "tp": self.tp, "rank": self.rank}

class JarFile(File):
    def __init__(self, name, path):
        super(JarFile, self).__init__(name, path, "JAR", 2)

class Directory(File):
    def __init__(self, name, path):
        super(Directory, self).__init__(name, path, "DIR", 1)

# file separator, regardless OS
SEP = "/"
ROOT = "ROOT"

# FileManager is responsible for processing requests and serving files.
# It also checks every step of fetching a list of directories.
class FileManager(object):
    def __init__(self, path):
        path = path.strip()
        if not self.checkPath(path):
            raise StandardError("Path " + path + " fails check and likely is incorrect")
        self.root = path

    @private
    def checkPath(self, path):
        ok = os.path.isabs(path)
        arr = path.split(os.sep)[1:]
        ok = reduce(lambda x, y: x and y, [ok] + [self.checkDirectory(elem) for elem in arr])
        return ok

    @private
    def checkDirectory(self, directory):
        prep = directory.strip()
        return len(prep) > 0 and prep != "." and prep != ".." and \
            re.match(r"^[^\*?!:;|\[\]/]+$", directory) is not None

    @private
    def sort(self, files):
        # sort function by rank and path name
        def compare(x, y):
            delta = x.rank - y.rank
            return cmp(x.path, y.path) if delta == 0 else delta
        return sorted(files, compare)

    @private
    def path(self, directory):
        directory = directory.strip()
        if not directory.startswith(ROOT):
            raise StandardError("Expected absolute directory, got " + directory)
        # root director is an empty string
        arr = directory.split(SEP)[1:]
        ok = reduce(lambda x, y: x and y, [True] + [self.checkDirectory(elem) for elem in arr])
        if not ok:
            raise StandardError("Directory " + directory + " is not correct")
        return [ROOT] + arr

    def breadcrumbs(self, directory, asdict=True):
        directory = directory if len(directory) > 0 else ROOT
        arr = self.path(directory)
        # merge every next instance with previous result
        dirs, path = [], None
        for elem in arr:
            path = SEP.join([path, elem]) if path else elem
            dr = File(elem, path, "FILE", 0)
            dirs.append(dr)
        if asdict:
            dirs = [x.toDict() for x in dirs]
        return dirs

    def list(self, directory, sort=True, asdict=True):
        directory = directory if len(directory) > 0 else ROOT
        arr = self.path(directory)[1:]
        fullpath = os.path.join(self.root, *arr)
        if not os.path.isdir(fullpath):
            raise StandardError("Filepath " + fullpath + " is not traversable")
        files = []
        for name in os.listdir(fullpath):
            interim = os.path.join(fullpath, name)
            path = self.path(directory) + [name]
            if os.path.isdir(interim):
                files.append(Directory(name, SEP.join(path)))
            elif interim.lower().endswith(".jar"):
                files.append(JarFile(name, SEP.join(path)))
        # sort if necessary
        if sort:
            files = self.sort(files)
        # convert each entry to dictionary
        if asdict:
            files = [x.toDict() for x in files]
        return files
