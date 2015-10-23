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

from types import DictType
from storagemanager import StorageManager

TEMPLATE_KEYSPACE = "TEMPLATE"

class Template(object):
    def __init__(self, uid, name, content):
        self.uid = uid
        self.name = name
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
            "content": self.content
        }

    @classmethod
    def fromDict(cls, obj):
        uid = obj["uid"]
        name = obj["name"]
        content = obj["content"]
        return cls(uid, name, content)

class TemplateManager(object):
    def __init__(self, storageManager):
        if type(storageManager) is not StorageManager:
            raise StandardError("Expected StorageManager, got " + str(type(storageManager)))
        self.storageManager = storageManager
