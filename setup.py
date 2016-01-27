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

import sys, os
from distutils.core import setup
from setuptools import Command
from config import GlobalConfig

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

# Additional custom commands
class StartOctohaven(Command):
    description = "Start Octohaven server"
    user_options = [
        ("host=", "h", "host to start server"),
        ("port=", "p", "port to start server"),
        ("spark-master=", "s", "Spark Master address, e.g. spark://..."),
        ("spark-ui=", "u", "Spark UI address, e.g. http://..."),
        ("jar-folder=", "j", "Jar root folder, e.g. /tmp/jars"),
        ("connection=", "c", "MySQL connection string, e.g. " +
            "jdbc:mysql://HOST:PORT/DATABASE?user=USER&password=PASSWORD")
    ]

    def initialize_options(self):
        self.host = None
        self.port = None
        self.spark_master = None
        self.spark_ui = None
        self.jar_folder = None
        self.connection = None

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
        # JAR_FOLDER
        if not self.jar_folder:
            print "[ERROR] Jar root folder is required, use --jar-folder=? to specify"
            sys.exit(1)
        # check that jar folder exists, absolute and open to read
        self.jar_folder = os.path.abspath(self.jar_folder) if self.jar_folder else None
        if not self.jar_folder or not os.path.exists(self.jar_folder):
            print "[ERROR] Jar folder must be set and be valid directory, got %s" % self.jar_folder
            sys.exit(1)
        if not os.access(self.jar_folder, os.R_OK):
            print "[ERROR] Permission denied (READ_ONLY) for %s" % self.jar_folder
            sys.exit(1)
        # MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD
        if not self.connection:
            print "[ERROR] MySQL connection string is required, use --connection=? to specify"
            sys.exit(1)

    def run(self):
        # overwrite parameters in configuration, so application will load it on the next step
        GlobalConfig.HOST = str(self.host)
        GlobalConfig.PORT = int(self.port)
        GlobalConfig.SPARK_MASTER_ADDRESS = self.spark_master
        GlobalConfig.SPARK_UI_ADDRESS = self.spark_ui
        GlobalConfig.JAR_FOLDER = self.jar_folder
        GlobalConfig.MYSQL_CONNECTION = self.connection
        # start service
        import src.octohaven as octohaven
        octohaven.run()

setup(
    name="octohaven",
    version=GlobalConfig.VERSION,
    description="Apache Spark job server",
    long_description="Apache Spark job server",
    author="Ivan Sadikov",
    author_email="isadikov@wynyardgroup.com",
    url="https://github.com/sadikovi/octohaven",
    platforms=["OS X", "Linux"],
    license="Apache License 2.0",
    cmdclass={
        "start_octohaven": StartOctohaven
    }
)
