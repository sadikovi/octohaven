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

# Global configuration that encapsulates all the main settings
class GlobalConfig(object):
    JSONIFY_PRETTYPRINT_REGULAR = False

    # Application version
    VERSION = "0.2.0.dev1"

    # root directory of the project
    ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

    # path to the configuration
    CONF_PATH = os.path.join(ROOT_PATH, "conf")
    CONF_NAME = "log.conf"

    # parameters to overwrite on application start
    HOST = None
    PORT = None
    SPARK_MASTER_ADDRESS = None
    SPARK_UI_ADDRESS = None
    JAR_FOLDER = None
    MYSQL_CONNECTION = None

# Configuration with testing mode on
class TestConfig(GlobalConfig):
    DEBUG = True
    TESTING = True

# Configuration for production
class ProductionConfig(GlobalConfig):
    DEBUG = False
    TESTING = False
