#!/usr/bin/env python

import os, re, math
from types import FileType, IntType
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
        # checks file path to ensure that it is absolute and does not contain illegal characters
        # or directories like ".."
        ok = os.path.isabs(path)
        arr = path.split(os.sep)[1:]
        ok = reduce(lambda x, y: x and y, [ok] + [self.checkDirectory(elem) for elem in arr])
        return ok

    @private
    def checkDirectory(self, directory):
        # checks directory name ensuring that it does not have illegal characters,
        # e.g. ";[]", ".."
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

    # resolves relative path into absolute path in current filesystem.
    # path can be a directory or file
    def resolveRelativePath(self, path):
        arr = path.split(SEP)
        if len(path) == 0 or not arr or len(arr) == 0:
            raise StandardError("Filepath appears to be empty")
        root = arr[0]
        if root != ROOT:
            raise StandardError("Filepath does not follow local pattern: " + path)
        absolutePath = os.path.join(self.root, *arr[1:])
        if not self.checkPath(absolutePath):
            raise StandardError("Filepath is not a valid system path: " + absolutePath)
        return absolutePath

    ############################################################
    ### Reading file API
    ############################################################
    # returns overall bytes in a file, also places cursor at the end of file, so you will have to
    # reposition it, if you want to read from arbitrary place
    @private
    def endOfFile(self, f):
        f.seek(0, 2)
        return f.tell()

    @private
    def startOfFile(self, f):
        return 0

    # validation of file
    def validateFile(self, f):
        if type(f) is not FileType:
            raise StandardError("Expected FileType, got %s" % str(type(f)))
        return f

    # validation of position
    def validatePosition(self, pos):
        if type(pos) is not IntType:
            raise StandardError("Expected IntType, got %s" % str(type(pos)))
        if pos < 0:
            raise StandardError("Position is negative")
        return pos

    # validation of page
    def validatePage(self, page):
        if type(page) is not IntType:
            raise StandardError("Expected IntType, got %s" % str(type(page)))
        if page < 0:
            raise StandardError("Page is negative")
        return page

    # returns at most number of pages for a file
    def numPages(self, f, chunk=500):
        fileSize = self.endOfFile(f)
        return math.ceil(fileSize * 1.0 / chunk)

    # generic function to read specific chunk of data
    # we always read from beginning
    @private
    def read(self, f, start, end):
        if start < 0 or end < 0 or start > end:
            raise StandardError("Wrong boundaries, start: %s, end: %s" % (start, end))
        f.seek(start, 0)
        return f.read(end - start)

    # generic method for reading a specific chunk of data from position
    # offset can be negative which tells us to read block before the position
    @private
    def readFromPosition(self, f, pos, offset=500):
        self.validateFile(f)
        self.validatePosition(pos)
        # start is always less than end in this case
        start, end = (pos, pos + offset) if offset > 0 else (pos + offset, pos)
        fileSize = self.endOfFile(f)
        if end < 0 or start > fileSize:
            return ""
        start = 0 if start < 0 else start
        end = fileSize if end > fileSize else end
        return self.read(f, start, end)

    # reading specific page from start, page number starts with 0 ->
    # offset indicates whether we need to truncate rows up to new line character
    def readFromStart(self, f, page, chunk=500, offset=0):
        start = chunk * page
        part = self.readFromPosition(f, start, chunk)
        if len(part) > 0:
            prefix = self.crop(f, start, -offset)
            suffix = self.crop(f, start + chunk, offset)
        else:
            prefix, suffix = "", ""
        return prefix + part + suffix

    # reading specific page from end, page number starts with 0 ->
    # offset indicates whether we need to truncate rows up to new line character
    def readFromEnd(self, f, page, chunk=500, offset=0):
        start = self.endOfFile(f) - chunk * (page + 1)
        part = self.readFromPosition(f, start, chunk)
        if len(part) > 0:
            prefix = self.crop(f, start, -offset)
            suffix = self.crop(f, start + chunk, offset)
        else:
            prefix, suffix = "", ""
        return prefix + part + suffix

    # truncate row by the closest new line character
    # used to return complete record instead of half of it
    def crop(self, f, pos, offset):
        part = self.readFromPosition(f, pos, offset)
        index = part.find(os.linesep)
        if index < 0:
            return part
        return part[index + 1:] if offset < 0 else part[:index]
