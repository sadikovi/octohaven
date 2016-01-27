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

import os, urllib2, json
from HTMLParser import HTMLParser
from types import ListType

class Tag(object):
    def __init__(self, tagname, attrs, data=None):
        self._tagname = tagname
        self._data = data
        self._attributes = {}
        for attr in attrs:
            self._attributes[str(attr[0]).lower()] = attr[1]
        self._children = []
    def getJSON(self):
        obj = {
            "tag": self._tagname,
            "data": self._data,
            "attributes": self._attributes,
            "children": [x.getJSON() for x in self._children]
        }
        return obj

class Parser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._stack = []
        self._root = []
        # tags to ignore while parsing
        self._ignore = ["html", "head", "link", "meta", "br"]
        # elements that do not have closed tag
        self._nonclosed = ["input", "img"]
    def handle_starttag(self, tag, attrs):
        if tag in self._ignore:
            return False
        tagobj = Tag(tag, attrs)
        if len(self._stack) == 0:
            self._root.append(tagobj)
        else:
            self._stack[-1]._children.append(tagobj)
        if tag not in self._nonclosed:
            self._stack.append(tagobj)
    def handle_endtag(self, tag):
        if tag in self._ignore:
            return False
        if len(self._stack) > 0 and self._stack[-1]._tagname == tag:
            self._stack.remove(self._stack[-1])
    def handle_data(self, data):
        if len(self._stack) > 0:
            self._stack[-1]._data = data.strip().replace("\n", "")
