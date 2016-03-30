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

import unittest, json
import src.utils as utils
from types import DictType
from src.octohaven import db
from src.template import Template

class TemplateTestSuite(unittest.TestCase):
    def setUp(self):
        Template.query.delete()
        self.opts = {"name": "test", "content": "{\"key\": \"value\"}"}

    def tearDown(self):
        pass

    def test_create(self):
        template = Template("name", 1L, "{\"key\": \"value\"}")
        self.assertEquals(template.name, "name")
        self.assertEquals(template.createtime, 1L)
        self.assertEquals(template.content, "{\"key\": \"value\"}")
        # test failures of createtime
        with self.assertRaises(StandardError):
            Template("name", 0L, "{\"key\": \"value\"}")
        with self.assertRaises(StandardError):
            Template("name", None, "{\"key\": \"value\"}")
        # test of empty name
        template = Template("", 1L, "{\"key\": \"value\"}")
        self.assertTrue(len(template.name) > 0)
        template = Template(None, 1L, "{\"key\": \"value\"}")
        self.assertTrue(len(template.name) > 0)

    def test_add(self):
        with self.assertRaises(StandardError):
            Template.create({"content": ""})
        with self.assertRaises(StandardError):
            Template.create({"name": ""})
        # test addition with default time
        template = Template.create(**self.opts)
        self.assertTrue(template.createtime > utils.currentTimeMillis() - 5000L)
        # test addition with fixed time
        opts = {"name": "test", "content": "{\"key\": \"value\"}"}
        template = Template.create(**opts)
        self.assertTrue(template.createtime > utils.currentTimeMillis() - 5000)
        # make sure that there are 2 entries in the table now
        arr = Template.list()
        self.assertTrue(len(arr) == 2)

    def test_list(self):
        for x in range(1, 6):
            self.opts["createtime"] = x
            Template.create(**self.opts)
        arr = Template.list()
        self.assertEquals(len(arr), 5)
        times = [x.createtime for x in arr]
        self.assertEquals(times, sorted(times, reverse=True))

    def test_get(self):
        template = Template.create(**self.opts)
        another = Template.get(template.uid)
        self.assertEquals(another.name, template.name)
        self.assertEquals(another.content, template.content)
        self.assertEquals(another.createtime, template.createtime)
        # should still fetch correct entry when searching by string
        another = Template.get("%s" % template.uid)
        self.assertEquals(another.json(), template.json())
        # should return None
        another = Template.get("abc")
        self.assertEquals(another, None)

    def test_delete(self):
        template = Template.create(**self.opts)
        res = Template.get(template.uid)
        self.assertTrue(res is not None)
        # after deleting template "get()" should return None
        Template.delete(template)
        res = Template.get(template.uid)
        self.assertTrue(res is None)

    def test_json(self):
        template = Template.create(**self.opts)
        another = Template.get(template.uid)
        obj = another.json()
        self.assertEquals(obj["uid"], another.uid)
        self.assertEquals(obj["name"], another.name)
        self.assertEquals(obj["createtime"], another.createtime)

# Load test suites
def _suites():
    return [
        TemplateTestSuite
    ]

# Load tests
def loadSuites():
    # global test suite for this module
    gsuite = unittest.TestSuite()
    for suite in _suites():
        gsuite.addTest(unittest.TestLoader().loadTestsFromTestCase(suite))
    return gsuite

if __name__ == '__main__':
    suite = loadSuites()
    print ""
    print "### Running tests ###"
    print "-" * 70
    unittest.TextTestRunner(verbosity=2).run(suite)
