#!/usr/bin/env python

import unittest, os, uuid, time
from paths import ROOT_PATH
from types import DictType
from src.redisconnector import RedisConnectionPool, RedisConnector
from src.storagemanager import StorageManager
from src.template import Template, TemplateManager
from src.utils import nextTemplateId, isTemplateId
from test.unittest_constants import RedisConst

class TemplateTestSuite(unittest.TestCase):
    def setUp(self):
        self.uid = nextTemplateId()
        self.name = "test-template"
        self.createtime = time.time()

    def tearDown(self):
        pass

    def test_create(self):
        template = Template(self.uid, self.name, self.createtime, {})
        self.assertEqual(template.uid, self.uid)
        self.assertEqual(template.name, self.name)
        self.assertEqual(template.content, {})
        # try storing list
        with self.assertRaises(StandardError):
            template = Template(self.uid, self.name, self.createtime, [])
        # try storing complex object
        template = Template(self.uid, self.name, self.createtime, {"list": [{"a": True}]})
        self.assertEqual(type(template.content), DictType)
        self.assertEqual(template.content["list"], str([{"a": True}]))

    # check that UID belongs to template group
    def test_tempalteUid(self):
        template = Template(self.uid, self.name, self.createtime, {})
        self.assertEqual(isTemplateId(template.uid), True)
        with self.assertRaises(StandardError):
            Template(uuid.uuid4().hex, self.name, self.createtime, {})

    def test_toDict(self):
        template = Template(self.uid, self.name, self.createtime, {})
        obj = template.toDict()
        self.assertEqual(obj["uid"], self.uid)
        self.assertEqual(obj["name"], self.name)
        self.assertEqual(obj["createtime"], long(self.createtime))
        self.assertEqual(obj["content"], {})

    def test_fromDict(self):
        template = Template(self.uid, self.name, self.createtime, {})
        obj = template.toDict()
        another = Template.fromDict(obj)
        self.assertEqual(another.toDict(), template.toDict())

class TemplateManagerTestSuite(unittest.TestCase):
    def setUp(self):
        test_pool = RedisConnectionPool({
            "host": RedisConst.redisHost(),
            "port": RedisConst.redisPort(),
            "db": RedisConst.redisTestDb()
        })
        self.connector = RedisConnector(test_pool)
        self.connector.flushdb()
        self.storageManager = StorageManager(self.connector)

    def tearDown(self):
        pass

    def test_init(self):
        templateManager = TemplateManager(self.storageManager)
        with self.assertRaises(StandardError):
            templateManager = TemplateManager(None)

    def test_createTemplate(self):
        templateManager = TemplateManager(self.storageManager)
        name = "test-template"
        content = {"a": True}
        template = templateManager.createTemplate(name, content)
        self.assertEqual(template.name, name)
        self.assertEqual(template.content, {"a": str(True)})

    def test_saveTemplate(self):
        templateManager = TemplateManager(self.storageManager)
        template = templateManager.createTemplate("test-template", {})
        templateManager.saveTemplate(template)
        self.assertEqual(len(templateManager.templates()), 1)
        self.assertEqual(templateManager.templateForUid(template.uid).toDict(), template.toDict())
        with self.assertRaises(StandardError):
            templateManager.saveTemplate(None)

    def test_templates(self):
        templateManager = TemplateManager(self.storageManager)
        template1 = templateManager.createTemplate("1-test-template", {})
        template2 = templateManager.createTemplate("2-test-template", {})
        templateManager.saveTemplate(template1)
        templateManager.saveTemplate(template2)
        arr = templateManager.templates()
        self.assertEqual([x.name for x in arr], ["1-test-template", "2-test-template"])

    def test_templateForUid(self):
        templateManager = TemplateManager(self.storageManager)
        self.assertEqual(templateManager.templateForUid(None), None)
        template = templateManager.createTemplate("test-template", {})
        templateManager.saveTemplate(template)
        self.assertEqual(templateManager.templateForUid(template.uid).toDict(), template.toDict())

    def test_deleteTemplate(self):
        templateManager = TemplateManager(self.storageManager)
        template = templateManager.createTemplate("test-template", {})
        templateManager.saveTemplate(template)
        self.assertEqual(len(templateManager.templates()), 1)
        templateManager.deleteTemplate(template)
        self.assertEqual(len(templateManager.templates()), 0)
        self.assertEqual(templateManager.templateForUid(template.uid).toDict(), template.toDict())

# Load test suites
def _suites():
    return [
        TemplateTestSuite,
        TemplateManagerTestSuite
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
