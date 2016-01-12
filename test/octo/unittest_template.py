#!/usr/bin/env python

import unittest, json, test, src.octo.storagesetup as setup, src.octo.utils as utils
from src.octo.mysqlcontext import MySQLContext, MySQLLock
from src.octo.storagemanager import StorageManager
from src.octo.template import Template, TemplateManager
from types import DictType

class TemplateTestSuite(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create(self):
        template = Template("id123", "test", 1L, {})
        self.assertEqual(template.uid, "id123")
        self.assertEqual(template.name, "test")
        self.assertEqual(template.content, {})
        # try storing list
        with self.assertRaises(StandardError):
            Template("id123", "test", 1L, [])
        # try storing complex object
        template = Template("id123", "test", 1L, {"list": [{"a": True}]})
        self.assertEqual(type(template.content), DictType)
        self.assertEqual(template.content["list"], str([{"a": True}]))

    def test_toJson(self):
        template = Template("id123", "test", 1L, {})
        obj = template.json()
        self.assertEqual(obj["uid"], "id123")
        self.assertEqual(obj["name"], "test")
        self.assertEqual(obj["createtime"], 1L)
        self.assertEqual(obj["content"], {})

    def test_toDict(self):
        template = Template("id123", "test", 1L, {"a": True, "b": 1})
        obj = template.dict()
        self.assertEqual(obj["uid"], "id123")
        self.assertEqual(obj["name"], "test")
        self.assertEqual(obj["createtime"], 1L)
        self.assertEqual(obj["content"], json.dumps({"a": True, "b": 1}))

    def test_fromDict(self):
        template = Template("id123", "test", 1L, {})
        obj = template.dict()
        another = Template.fromDict(obj)
        self.assertEqual(another.dict(), template.dict())

class TemplateManagerTestSuite(unittest.TestCase):
    def setUp(self):
        config = {
            "host": test.Settings.mp().get("host"),
            "port": test.Settings.mp().get("port"),
            "user": test.Settings.mp().get("user"),
            "password": test.Settings.mp().get("password"),
            "database": test.Settings.mp().get("database")
        }
        MySQLLock.reset()
        sqlcnx = MySQLContext(**config)
        setup.loadTables(sqlcnx, drop_existing=True, logging=False)
        self.storageManager = StorageManager(sqlcnx)

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
        self.assertEqual(template.content, {"a": True})

    def test_saveTemplate(self):
        templateManager = TemplateManager(self.storageManager)
        template = templateManager.createTemplate("test-template", {})
        self.assertEqual(len(templateManager.templates()), 1)
        self.assertEqual(templateManager.templateForUid(template.uid).dict(), template.dict())
        with self.assertRaises(StandardError):
            templateManager.saveTemplate(None)

    def test_templates(self):
        templateManager = TemplateManager(self.storageManager)
        template1 = templateManager.createTemplate("1-test-template", {})
        template2 = templateManager.createTemplate("2-test-template", {})
        arr = templateManager.templates()
        self.assertEqual([x.name for x in arr], ["1-test-template", "2-test-template"])

    def test_templateForUid(self):
        templateManager = TemplateManager(self.storageManager)
        self.assertEqual(templateManager.templateForUid(None), None)
        template = templateManager.createTemplate("test-template", {})
        self.assertEqual(templateManager.templateForUid(template.uid).dict(), template.dict())

    def test_deleteTemplate(self):
        templateManager = TemplateManager(self.storageManager)
        template = templateManager.createTemplate("test-template", {})
        self.assertEqual(len(templateManager.templates()), 1)
        templateManager.deleteTemplate(template.uid)
        self.assertEqual(len(templateManager.templates()), 0)
        self.assertEqual(templateManager.templateForUid(template.uid), None)

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
