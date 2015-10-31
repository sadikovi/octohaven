#!/usr/bin/env python

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

import uuid
from types import DictType, StringType
from storagemanager import StorageManager
from utils import *

TEMPLATE_KEYSPACE = "TEMPLATE"
TEMPLATE_NAME_UNKNOWN = "Unknown"

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

    def toDict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "createtime": self.createtime,
            "content": self.content
        }

    @classmethod
    def fromDict(cls, obj):
        uid = obj["uid"]
        name = obj["name"]
        createtime = obj["createtime"]
        content = obj["content"]
        return cls(uid, name, createtime, content)

class TemplateManager(object):
    def __init__(self, storageManager):
        if type(storageManager) is not StorageManager:
            raise StandardError("Expected StorageManager, got " + str(type(storageManager)))
        self.storageManager = storageManager

    def createTemplate(self, name, content):
        uid = "template_" + uuid.uuid4().hex
        # we use default name if current name cannot be resolved
        name = name if type(name) is StringType and len(name) > 0 else TEMPLATE_NAME_UNKNOWN
        # creation time in milliseconds
        createtime = currentTimeMillis()
        # check that content is a dictionary
        if type(content) is not DictType:
            raise StandardError("Content is wrong and cannot be parsed")
        return Template(uid, str(name), createtime, content)

    def saveTemplate(self, template):
        self.storageManager.saveItem(template, klass=Template)
        self.storageManager.addItemToKeyspace(TEMPLATE_KEYSPACE, template.uid)

    def templates(self):
        # we retrieve all the templates, do not limit them.
        # sort templates by name
        def func(x, y):
            return cmp(x.name, y.name)
        return self.storageManager.itemsForKeyspace(TEMPLATE_KEYSPACE, -1, func, klass=Template)

    def templateForUid(self, uid):
        return self.storageManager.itemForUid(uid, klass=Template)

    # we do not really delete template, we just remove reference to it from keyspace
    def deleteTemplate(self, template):
        if type(template) is not Template:
            raise StandardError("Expected Template, found " + str(type(template)))
        self.storageManager.removeItemFromKeyspace(TEMPLATE_KEYSPACE, template.uid)
