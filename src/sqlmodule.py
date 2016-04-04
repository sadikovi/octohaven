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

from flask_sqlalchemy import SQLAlchemy

# `MySQLContext` is the main entry and wrapper to deal with storing and retrieving data from MySQL.
# It maintains connection pool and handles new connection allocations automatically.
# There is only one context per application, therefore should be created globally; it is not
# restricted currently, but will be added in the future.
# Configuration parameters: ["app", "host", "port", "user", "password", "database"]
def MySQLContext(**config):
    # Binding application
    app = config["application"]
    # Minimum pool size
    min_pool_size = config["pool_size"] if "pool_size" in config else 5
    # Debug mode for SQL context, will log all queries
    debug = app.config["TESTING"] if "TESTING" in app.config else False

    app.config["SQLALCHEMY_DATABASE_URI"] = engine(config)
    app.config["SQLALCHEMY_ECHO"] = debug
    app.config["SQLALCHEMY_POOL_SIZE"] = min_pool_size
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config["SQLALCHEMY_MAX_OVERFLOW"] = 10
    # initialize db for application
    return SQLAlchemy(app)

# MySQL engine, e.g. mysql://scott:tiger@localhost/mydatabase
def engine(conf):
    return "mysql+mysqlconnector://%(user)s:%(password)s@%(host)s:%(port)s/%(database)s" % (conf)
