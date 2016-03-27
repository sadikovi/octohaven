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

import utils
from flask import json
from sqlalchemy import desc
from octohaven import db, api

class Template(db.Model):
    # Unique template key
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Name of the template
    name = db.Column(db.String(255), nullable=False)
    # Date when template was created in milliseconds
    createtime = db.Column(db.BigInteger, nullable=False)
    # Content (json string)
    content = db.Column(db.String(4000), nullable=True)

    def __init__(self, name, createtime, content):
        self.name = utils.getCanonicalName(name)
        if not createtime > 0:
            raise StandardError("Create time must be > 0, got %s" % createtime)
        self.createtime = createtime
        self.content = content

    @classmethod
    @utils.sql
    def create(cls, **opts):
        # `opts` are expected to have "name" and content, and createtime, unless empty
        if "name" not in opts:
            raise StandardError("Expected 'name' key in %s" % json.dumps(opts))
        if "content" not in opts:
            raise StandardError("Expected 'content' key in %s" % json.dumps(opts))
        # Create new template
        template = cls(name=opts["name"], createtime=utils.currentTimeMillis(),
            content=opts["content"])
        db.session.add(template)
        db.session.commit()
        return template

    @classmethod
    @utils.sql
    def list(cls):
        return cls.query.order_by(desc(cls.createtime)).all()

    @classmethod
    @utils.sql
    def get(cls, uid):
        return cls.query.get(uid)

    @classmethod
    @utils.sql
    def delete(cls, template):
        db.session.delete(template)
        db.session.commit()

    def json(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "createtime": self.createtime,
            "content": json.loads(self.content),
            "delete_url": api("/template/delete/%s" % self.uid),
            "delete_and_list_url": api("/template/delete_and_list/%s" % self.uid)
        }
