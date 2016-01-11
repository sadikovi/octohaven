#!/usr/bin/env python

import json, src.octo.utils as utils
from types import DictType
from src.octo.mysqlcontext import MySQLContext

TEMPLATE_DEFAULT_NAME = "Unknown"

# Templates is a add-on functionality that saves all job parameters as a template job.
# You can request it later in order to populate UI forms and all, minimizing filling up time. It is
# different from a job, as template is non validated set of parameters, unlike job, e.g. dumping
# all the fields we received into object and store it somewhere; you should be able to create
# templates, even if creation of a job fails, or fill just half of the forms.
# Templates are stores as `Template` objects that look like this:
# {
#   "uid": template_****************,
#   "name": "Cool template"
#   "content": {
#       some object with all the parameters that we received
#   }
# }
class Template(object):
    def __init__(self, uid, name, createtime, content):
        self.uid = uid
        self.name = name
        self.createtime = long(createtime)
        if type(content) is not DictType:
            raise StandardError("Template expected DictType, got " + str(type(content)))
        self.content = {}
        # make sure that fields in content are strings and do not have nested structure
        for key, value in content.items():
            self.content[str(key)] = str(value)

    def json(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "createtime": self.createtime,
            "content": self.content
        }

    # flat dictionary of properties
    def dict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "createtime": self.createtime,
            "content": json.dumps(self.content)
        }

    @classmethod
    def fromDict(cls, obj):
        # validate template uid to fetch only Template instances
        uid = obj["uid"]
        name = obj["name"]
        createtime = long(obj["createtime"])
        content = utils.jsonOrElse(obj["content"], None)
        if not content:
            raise StandardError("Could not process content %s" % obj["content"])
        return cls(uid, name, createtime, content)

# Template manager for creating, updating, and removing templates. Uses sql context to interact with
# storage. Note that sql context is one for entire application
class TemplateManager(object):
    def __init__(self, sqlContext):
        utils.assertInstance(sqlContext, SQLContext)
        self.sqlcnx = sqlContext

    def createTemplate(self, name, content):
        # we use default name if current name cannot be resolved
        name = str(name).strip()
        name = name if len(name) > 0 else TEMPLATE_DEFAULT_NAME
        # creation time in milliseconds
        createtime = utils.currentTimeMillis()
        # check that content is a dictionary
        assertType(content, DictType, "Content is wrong and cannot be parsed: %s" % type(content))
        # insert into templates table
        pr = {"name": name, "createtime": createtime, "content": json.dumps(content)}
        uid = sqlcnx.insert("templates", pr)
        return Template(uid, name, createtime, content)

    def templates(self):
        # we retrieve all the templates, do not limit them.
        # sort templates by name
        def func(x, y):
            return cmp(x.name, y.name)
        keyspace = self.keyspace(TEMPLATE_KEYSPACE)
        return self.storageManager.itemsForKeyspace(keyspace, -1, func, klass=Template)

    def templateForUid(self, uid):
        return self.storageManager.itemForUid(uid, klass=Template)

    def deleteTemplate(self, template):
        assertType(template, Template)
        keyspace = self.keyspace(TEMPLATE_KEYSPACE)
        self.storageManager.removeItemFromKeyspace(keyspace, template.uid)
