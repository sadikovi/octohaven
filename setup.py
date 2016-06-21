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

import re, sys, os, src.utils as utils
from distutils.core import setup
from setuptools import Command
from version import VERSION
from internal import Options, LIB_PATH, DEFAULT_WORKING_DIR, DEFAULT_SPARK_SUBMIT, DEFAULT_NUM_SLOTS

# Only Python 2.7 is supported
PYTHON_VERSION_MAJOR = 2
PYTHON_VERSION_MINOR = 7
if sys.version_info.major != PYTHON_VERSION_MAJOR or sys.version_info.minor != PYTHON_VERSION_MINOR:
    print "[ERROR] Only Python %s.%s is supported" % (PYTHON_VERSION_MAJOR, PYTHON_VERSION_MINOR)
    sys.exit(1)

# We run only on OS X and Linux
if not (sys.platform.startswith("darwin") or sys.platform.startswith("linux")):
    print "[ERROR] Only OS X and Linux are supported"
    sys.exit(1)

# Add dependencies to the path, could not figure out how to make setup.py load libraries
sys.path.insert(1, LIB_PATH)

# Additional custom commands
class StartOctohaven(Command):
    description = "Start Octohaven server"
    user_options = [
        ("host=", "h", "host to start server"),
        ("port=", "p", "port to start server"),
        ("spark-master=", "s", "Spark Master address, e.g. spark://..."),
        ("spark-ui=", "u", "Spark UI address, e.g. http://..."),
        ("spark-submit=", "r", "Spark submit path, default is 'spark-submit'"),
        ("jar-folder=", "j", "Jar root folder, e.g. /tmp/jars"),
        ("working-dir=", "w", "Working directory, default is ./work/"),
        ("num-slots=", "n", "Number of slots, default is 1"),
        ("connection=", "c", "MySQL connection string, e.g. " +
            "jdbc:mysql://HOST:PORT/DATABASE?user=USER&password=PASSWORD"),
        ("test", "t", "Test mode, runs unit-tests for the application")
    ]

    def initialize_options(self):
        self.host = None
        self.port = None
        self.spark_master = None
        self.spark_ui = None
        self.spark_submit = None
        self.jar_folder = None
        self.connection = None
        # Misc
        self.test = False
        # Working directory
        self.working_dir = None
        # Number of slots
        self.num_slots = None

    def finalize_options(self):
        # OCTOHAVEN_HOST
        if not self.host:
            print "[ERROR] Host is required, use --host=? to specify"
            sys.exit(1)
        # OCTOHAVEN_PORT
        if not self.port:
            print "[ERROR] Port is required, use --port=? to specify"
            sys.exit(1)
        if not self.port.isdigit():
            print "[ERROR] Invalid port (%s)" % self.port
            sys.exit(1)
        # OCTOHAVEN_SPARK_MASTER_ADDRESS
        if not self.spark_master:
            print "[ERROR] Spark Master address is required, use --spark-master=? to specify"
            sys.exit(1)
        # OCTOHAVEN_SPARK_UI_ADDRESS
        if not self.spark_ui:
            print "[ERROR] Spark UI address is required, use --spark-ui=? to specify"
            sys.exit(1)
        # SPARK_SUBMIT (not a configuration option)
        if not self.spark_submit:
            print "[WARN] Submit is not specified, fall back to default 'spark-submit'"
            self.spark_submit = DEFAULT_SPARK_SUBMIT
        # JAR_FOLDER
        if not self.jar_folder:
            print "[ERROR] Jar root folder is required, use --jar-folder=? to specify"
            sys.exit(1)
        # Check that jar folder exists, absolute and open to read
        self.jar_folder = os.path.realpath(os.path.abspath(str(self.jar_folder)))
        if not os.path.isdir(self.jar_folder):
            print "[ERROR] Jar folder must be valid directory, got '%s'" % self.jar_folder
            sys.exit(1)
        if not os.access(self.jar_folder, os.R_OK):
            print "[ERROR] Permission READ_ONLY denied for %s" % self.jar_folder
            sys.exit(1)
        # Working directory, if not specified then default working directory is used
        self.working_dir = os.path.realpath(os.path.abspath(str(self.working_dir))) \
            if self.working_dir else DEFAULT_WORKING_DIR
        if not os.path.isdir(self.working_dir):
            print "[ERROR] Working directory must be a valid directory, got '%s'" % self.working_dir
            sys.exit(1)
        if not os.access(self.working_dir, os.R_OK) or not os.access(self.working_dir, os.W_OK):
            print "[ERROR] Insufficient permissions, READ_WRITE denied for %s" % self.working_dir
            sys.exit(1)
        # Number of slots
        self.num_slots = utils.intOrElse(self.num_slots, DEFAULT_NUM_SLOTS)
        # MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD
        if not self.connection:
            print "[ERROR] MySQL connection string is required, use --connection=? to specify"
            sys.exit(1)
        # Assign dictionary of values instead of connection string
        self.connection = utils.validateMySQLJDBC(self.connection)

    def run(self):
        # Overwrite parameters in configuration, so application will load it on the next step
        Options.HOST = str(self.host)
        Options.PORT = int(self.port)
        Options.SPARK_MASTER_ADDRESS = self.spark_master
        Options.SPARK_UI_ADDRESS = self.spark_ui
        Options.SPARK_SUBMIT = self.spark_submit
        Options.JAR_FOLDER = self.jar_folder
        # Application Spark logs directory
        Options.WORKING_DIR = self.working_dir
        # Number of slots
        Options.NUM_SLOTS = int(self.num_slots)
        # Assign MySQL settings
        Options.MYSQL_HOST = self.connection["host"]
        Options.MYSQL_PORT = self.connection["port"]
        Options.MYSQL_DATABASE = self.connection["database"]
        Options.MYSQL_USER = self.connection["user"]
        Options.MYSQL_PASSWORD = self.connection["password"]
        # Start service
        import src.octohaven as octohaven
        if self.test:
            octohaven.test()
        else:
            octohaven.start()

class UpdateVersion(Command):
    description = "BUILD update Octohaven version"
    user_options = [
        ("version=", "v", "new version")
    ]

    # Parse version of major.minor.patch format
    def parseVersion(self, version):
        mtch = re.match("^(\d+)\.(\d+)\.(\d+)$", version)
        if not mtch:
            raise StandardError("Invalid version %s, cannot parse" % version)
        major = int(mtch.group(1))
        minor = int(mtch.group(2))
        patch = int(mtch.group(3))
        # return tuple
        return (major, minor, patch)

    # Find `orig` in a file and replace it with `updated` in place
    def findAndReplace(self, path, orig, updated):
        arr = []
        with open(path, 'r') as f:
            for line in f:
                line = line.replace(orig, updated) if orig in line else line
                arr.append(line)
        # write it back into file
        with open(path, 'w') as f:
            for line in arr:
                f.write(line)


    def initialize_options(self):
        self.version = "x.y.z"
        self.major = None
        self.minor = None
        self.patch = None

    def finalize_options(self):
        res = self.parseVersion(self.version)
        (self.major, self.minor, self.patch) = res

    def run(self):
        result = self.parseVersion(VERSION)
        (major, minor, patch) = result
        major = self.major if self.major >= 0 else major
        minor = self.minor if self.minor >= 0 else minor
        patch = self.patch if self.patch >= 0 else patch
        UPDATED_VERSION = "%s.%s.%s" % (major, minor, patch)
        if VERSION == UPDATED_VERSION:
            print "No update for %s" % VERSION
            return
        print "Updating version %s to %s" % (VERSION, UPDATED_VERSION)
        # We need to substitute version in 3 files: version.py, package.json, bower.json
        self.findAndReplace("version.py", VERSION, UPDATED_VERSION)
        self.findAndReplace("package.json", "\"version\": \"%s\"" % VERSION,
            "\"version\": \"%s\"" % UPDATED_VERSION)
        self.findAndReplace("bower.json", "\"version\": \"%s\"" % VERSION,
            "\"version\": \"%s\"" % UPDATED_VERSION)

setup(
    name="octohaven",
    version=VERSION,
    description="Apache Spark job server",
    long_description="Apache Spark job server",
    author="Ivan Sadikov",
    author_email="isadikov@wynyardgroup.com",
    url="https://github.com/sadikovi/octohaven",
    platforms=["OS X", "Linux"],
    license="Apache License 2.0",
    cmdclass={
        "start_octohaven": StartOctohaven,
        "update_version": UpdateVersion
    }
)
