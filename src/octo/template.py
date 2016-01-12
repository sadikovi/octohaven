#!/usr/bin/env python

import json, src.octo.utils as utils
from types import DictType, NoneType, BooleanType, IntType, LongType, FloatType
from src.octo.mysqlcontext import MySQLContext
from src.octo.storagemanager import StorageManager

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
        utils.assertInstance(content, DictType,
            "Template expected DictType, got %s" % type(content))
        self.content = {}
        # make sure that fields in content are primitive types and do not have nested structure
        for key, value in content.items():
            if isinstance(value, NoneType) or isinstance(value, BooleanType) or \
                isinstance(value, IntType) or isinstance(value, LongType) or \
                isinstance(value, FloatType):
                self.content[str(key)] = value
            else:
                self.content[str(key)] = str(value)

    # json representation of Template
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
        if content is None:
            raise StandardError("Could not process content %s" % obj["content"])
        return cls(uid, name, createtime, content)

# Template manager for creating, updating, and removing templates. Uses sql context to interact with
# storage. Note that sql context is one for entire application
class TemplateManager(object):
    def __init__(self, storageManager):
        utils.assertInstance(storageManager, StorageManager)
        self.storage = storageManager

    # Return newly created Template object that is already stored
    def createTemplate(self, name, content):
        # we use default name if current name cannot be resolved
        name = str(name).strip()
        name = name if len(name) > 0 else TEMPLATE_DEFAULT_NAME
        # creation time in milliseconds
        createtime = utils.currentTimeMillis()
        # check that content is a dictionary
        utils.assertInstance(content, DictType,
            "Content is wrong and cannot be parsed: %s" % type(content))
        # insert into templates table
        uid = self.storage.createTemplate(name, createtime, json.dumps(content))
        return Template(uid, name, createtime, content)

    # Retrieve all the templates, do not limit them, also sort templates by name, this is done on
    # sql level in storage manager. Return them as list of Template objects, results is guaranteed
    # to be a list
    def templates(self):
        # rows is a list of templates
        rows = self.storage.getTemplates()
        if not rows:
            rows = []
        # convert every row into Template object
        return map(lambda row: Template.fromDict(row), rows)

    # Retrieve template for a specific uid. Return Template object, if found, otherwise None
    def templateForUid(self, uid):
        row = self.storage.getTemplate(uid)
        return Template.fromDict(row) if row else None

    # Delete template for a specific uid
    def deleteTemplate(self, uid):
        self.storage.deleteTemplate(uid)
