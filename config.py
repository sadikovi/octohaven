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

# Root directory of the project
ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
# Dependencies directory
LIB_PATH = os.path.join(ROOT_PATH, "lib")
# Path to the configuration
CONF_PATH = os.path.join(ROOT_PATH, "conf")
CONF_NAME = "log.conf"
# Default application Spark logs directory
DEFAULT_WORKING_DIR = os.path.join(ROOT_PATH, "work")
# Default 'spark-submit' command
DEFAULT_SPARK_SUBMIT = "spark-submit"

# Global configuration that encapsulates all the main settings
class Options(object):
    # Flask options
    JSONIFY_PRETTYPRINT_REGULAR = False
    # Parameters to overwrite on application start
    HOST = None
    PORT = None
    SPARK_MASTER_ADDRESS = None
    SPARK_UI_ADDRESS = None
    SPARK_SUBMIT = None
    JAR_FOLDER = None
    # Working directory for Spark logs, and etc
    WORKING_DIR = None
    # MySQL settings
    MYSQL_HOST = None
    MYSQL_PORT = None
    MYSQL_DATABASE = None
    MYSQL_USER = None
    MYSQL_PASSWORD = None
    # MySQL schema reset (if True then drops and recreates table every time service is launched)
    MYSQL_SCHEMA_RESET = False

    # Turn options off for distribution, DEBUG option results in reloading server, which sqlalchemy
    # does not like and freezes occasionally, and it is not that useful anyway, so we keep it False
    DEBUG = False
    # Testing results in verbose log output from flask and sqlalchemy, so it is recommended to
    # turn them off when creating distribution
    TESTING = True
