#!/usr/bin/env python

#
# Copyright 2015 sadikovi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os, copy, re, math, utils
from types import FileType, IntType

# FileManager is responsible for processing requests and serving files.
# It also checks every step of fetching a list of directories.
# "extensions" is a list of allowed extensions to keep, directories are always kept
class FileManager(object):
    def __init__(self, path, alias="/home", extensions=[]):
        path = os.path.realpath(str(path).strip())
        if not os.path.isabs(path):
            raise StandardError("Path '%s' is not absolute" % path)
        if not os.path.isdir(path):
            raise StandardError("Path '%s' is not a directory" % path)
        alias = str(alias).strip()
        if not alias:
            raise StandardError("Unspecified alias")
        self.home = path
        self.alias = alias
        self.extensions = extensions

    # Check whether path is sub-path of "self.home"
    def issubpath(self, path):
        fullpath = os.path.realpath(path)
        return os.path.commonprefix([fullpath, self.home]) == self.home

    # Traverse directory and return list of resolved file paths and tree of paths from self.home to
    # current directory. "parts" arguments are names of directories to traverse from self.home to
    # last part.
    def ls(self, *parts):
        # check that parts do not contain empty strings
        parts = list(parts)
        for part in parts:
            if not part:
                raise StandardError("Empty part in %s" % parts)
        # building tree to traverse back and forth as breadcrumbs
        aggpath = self.home
        tree = [{"type": "dir", "isdir": True, "name": "home", "url": self.alias}]
        for part in parts:
            aggpath = os.path.realpath(os.path.join(aggpath, part))
            if not os.path.isdir(aggpath):
                raise StandardError("Directory '%s' is not valid" % aggpath)
            if not self.issubpath(aggpath):
                raise StandardError("403, Forbidden")
            relpath = os.path.relpath(aggpath, self.home)
            tree.append({"type": "dir", "isdir": True, "name": part,
                "url": os.path.join(self.alias, relpath)})
        lstree = []
        # append special links such as ".." and ".", if any exists
        if len(tree) >= 1:
            obj = copy.copy(tree[-1])
            obj["name"] = "."
            lstree.append(obj)
        if len(tree) >= 2:
            obj = copy.copy(tree[-2])
            obj["name"] = ".."
            lstree.append(obj)
        # building list of files and subdirectories
        for name in os.listdir(aggpath):
            currentpath = os.path.join(aggpath, name)
            if not self.issubpath(currentpath):
                raise StandardError("403, Forbidden")
            tp = "dir" if os.path.isdir(currentpath) else os.path.splitext(name)[1]
            # filter out extensions, keep directories and any extensions specified
            if not self.extensions or tp == "dir" or tp in self.extensions:
                relpath = os.path.relpath(currentpath, self.home)
                lstree.append({"type": tp, "isdir": tp == "dir", "name": name,
                    "url": os.path.join(self.alias, relpath)})
        # sort list: directories first, then files in lexicographical order by name
        def lscmp(x, y):
            if x["type"] == y["type"] == "dir" or x["type"] != "dir" and y["type"] != "dir":
                return cmp(x["name"], y["name"])
            else:
                return -1 if x["type"] == "dir" else 1
        lstree = sorted(lstree, cmp=lscmp)
        return (tree, lstree)

    ############################################################
    ### Reading file API
    ############################################################
    # Return overall bytes in a file, also places cursor at the end of file, so you will have to
    # reposition it, if you want to read from arbitrary place
    def endOfFile(self, f):
        f.seek(0, 2)
        return f.tell()

    def startOfFile(self, f):
        return 0

    # Validation of file
    def validateFile(self, f):
        utils.assertInstance(f, FileType)
        return f

    # Validation of position
    def validatePosition(self, pos):
        utils.assertInstance(pos, IntType)
        if pos < 0:
            raise StandardError("Position '%s' is negative" % pos)
        return pos

    # Validation of page
    def validatePage(self, page):
        utils.assertInstance(page, IntType)
        if page <= 0:
            raise StandardError("Page is not positive")
        return page

    # Return at most number of pages for a file
    def numPages(self, f, chunk=500):
        fileSize = self.endOfFile(f)
        # if file is empty, we still treat it as having at most 1 page
        return int(math.ceil(fileSize * 1.0 / chunk)) if fileSize > 0 else 1

    # Generic function to read specific chunk of data
    # we always read from beginning
    def read(self, f, start, end):
        if start < 0 or end < 0 or start > end:
            raise StandardError("Wrong boundaries, start: %s, end: %s" % (start, end))
        f.seek(start, 0)
        return f.read(end - start)

    # Generic method for reading a specific chunk of data from position
    # offset can be negative which tells us to read block before the position
    def readFromPosition(self, f, pos, offset=500):
        self.validateFile(f)
        # remove position validation and replace with just type check, since we deal with negative
        # positions in code
        utils.assertInstance(pos, IntType)
        # start is always less than end in this case
        start, end = (pos, pos + offset) if offset > 0 else (pos + offset, pos)
        fileSize = self.endOfFile(f)
        if end < 0 or start > fileSize:
            return ""
        start = 0 if start < 0 else start
        end = fileSize if end > fileSize else end
        return self.read(f, start, end)

    # Reading specific page from start, page number starts with 1 ->
    # offset indicates whether we need to truncate rows up to new line character
    # chunk is a block to read in bytes
    def readFromStart(self, f, page, chunk=500, offset=0):
        self.validatePage(page)
        numPages = self.numPages(f, chunk)
        if page > numPages:
            raise StandardError("Page '%s' exceeds max number of pages" % page)
        start = chunk * (page - 1)
        part = self.readFromPosition(f, start, chunk)
        if len(part) > 0:
            prefix = self.crop(f, start, -offset)
            suffix = self.crop(f, start + chunk, offset)
        else:
            prefix, suffix = "", ""
        return prefix + part + suffix

    # Reading specific page from end, page number starts with 1 ->
    # offset indicates whether we need to truncate rows up to new line character
    # chunk is a block to read in bytes
    def readFromEnd(self, f, page, chunk=500, offset=0):
        self.validatePage(page)
        numPages = self.numPages(f, chunk)
        if page > numPages:
            raise StandardError("Page '%s' exceeds max number of pages" % page)
        start = self.endOfFile(f) - chunk * page
        part = self.readFromPosition(f, start, chunk)
        if len(part) > 0:
            prefix = self.crop(f, start, -offset)
            suffix = self.crop(f, start + chunk, offset)
        else:
            prefix, suffix = "", ""
        return prefix + part + suffix

    # Truncate row by the closest new line character
    # used to return complete record instead of half of it
    def crop(self, f, pos, offset):
        part = self.readFromPosition(f, pos, offset)
        index = part.find(os.linesep)
        if index < 0:
            return part
        return part[index + 1:] if offset < 0 else part[:index]
