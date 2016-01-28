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

import os

################################################################
# Internal configuration
################################################################

# Application version
VERSION = "0.2.0.dev1"

# Root directory of the project
ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

# Path to the configuration
CONF_PATH = os.path.join(ROOT_PATH, "conf")
CONF_NAME = "log.conf"

# Global configuration that encapsulates all the main settings
class Options(object):
    # Flask options
    JSONIFY_PRETTYPRINT_REGULAR = False
    # Parameters to overwrite on application start
    HOST = None
    PORT = None
    SPARK_MASTER_ADDRESS = None
    SPARK_UI_ADDRESS = None
    JAR_FOLDER = None
    # MySQL settings
    MYSQL_HOST = None
    MYSQL_PORT = None
    MYSQL_DATABASE = None
    MYSQL_USER = None
    MYSQL_PASSWORD = None

# Configuration with testing mode on
class TestConfig(Options):
    DEBUG = True
    TESTING = True

# Configuration for production
class ProductionConfig(Options):
    DEBUG = False
    TESTING = False
