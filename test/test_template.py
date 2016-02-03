#!/usr/bin/env python

import unittest, json
from src.octohaven import sqlContext
from src.sqlschema import loadSchema
from src.template import Template, TemplateManager
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

    def test_json(self):
        template = Template("id123", "test", 1L, {})
        obj = template.json()
        self.assertEqual(obj["uid"], "id123")
        self.assertEqual(obj["name"], "test")
        self.assertEqual(obj["createtime"], 1L)
        self.assertEqual(obj["content"], {})

    def test_dict(self):
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
        loadSchema(sqlContext, True, True)

    def tearDown(self):
        pass

    def test_createTemplate(self):
        templateManager = TemplateManager(sqlContext)
        name = "test-template"
        content = {"a": True}
        template = templateManager.createTemplate(name, content)
        self.assertEqual(template.name, name)
        self.assertEqual(template.content, {"a": True})

    def test_saveTemplate(self):
        templateManager = TemplateManager(sqlContext)
        template = templateManager.createTemplate("test-template", {})
        self.assertEqual(len(templateManager.templates()), 1)
        self.assertEqual(templateManager.templateForUid(template.uid).dict(), template.dict())
        with self.assertRaises(StandardError):
            templateManager.saveTemplate(None)

    def test_templateForUid(self):
        templateManager = TemplateManager(sqlContext)
        self.assertEqual(templateManager.templateForUid(None), None)
        template = templateManager.createTemplate("test-template", {})
        self.assertEqual(templateManager.templateForUid(template.uid).dict(), template.dict())

    def test_templates(self):
        templateManager = TemplateManager(sqlContext)
        template1 = templateManager.createTemplate("1-test-template", {})
        template2 = templateManager.createTemplate("2-test-template", {})
        arr = templateManager.templates()
        self.assertEqual([x.name for x in arr], ["1-test-template", "2-test-template"])

    def test_deleteTemplate(self):
        templateManager = TemplateManager(sqlContext)
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
