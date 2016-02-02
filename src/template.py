#!/usr/bin/env python

import json, utils
from types import DictType, NoneType, BooleanType, IntType, LongType, FloatType
from octohaven import sqlContext
from extlogging import Loggable

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
class TemplateManager(Loggable, object):
    def __init__(self):
        super(TemplateManager, self).__init__()

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
        rowid = None
        with sqlContext.cursor(with_transaction=True) as cr:
            dml = ("INSERT INTO templates(name, createtime, content) "
                    "VALUES(%(name)s, %(createtime)s, %(content)s)")
            cr.execute(dml, {"name": name, "createtime": createtime,
                "content": json.dumps(content)})
            rowid = cr.lastrowid
        return Template(rowid, name, createtime, content)

    # Retrieve template for a specific uid. Return Template object, if found, otherwise None
    def templateForUid(self, uid):
        row = None
        with sqlContext.cursor(with_transaction=False) as cr:
            sql = "SELECT uid, name, createtime, content FROM templates WHERE uid = %(uid)s"
            cr.execute(sql, {"uid": uid})
            row = cr.fetchone()
        return Template.fromDict(row) if row else None

    # Retrieve all the templates, do not limit them, also sort templates by name, this is done on
    # sql level in storage manager. Return them as list of Template objects, results is guaranteed
    # to be a list
    def templates(self):
        # rows is a list of templates
        rows = None
        with sqlContext.cursor(with_transaction=False) as cr:
            sql = "SELECT uid, name, createtime, content FROM templates ORDER BY name ASC"
            cr.execute(sql)
            rows = cr.fetchall()
        # convert every row into Template object
        return map(lambda row: Template.fromDict(row), rows) if rows else []

    # Delete template for a specific uid
    def deleteTemplate(self, uid):
        with sqlContext.cursor(with_transaction=True) as cr:
            dml = "DELETE FROM templates WHERE uid = %(uid)s"
            cr.execute(dml, {"uid": uid})
