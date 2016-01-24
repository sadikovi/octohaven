#!/usr/bin/env python

import sys, os
from distutils.core import setup
from setuptools import Command
from info import VERSION

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
class StartServer(Command):
    description = "Start octohaven server"
    user_options = [
        ("host=", "h", "host to start server"),
        ("port=", "p", "port to start server")
    ]

    def initialize_options(self):
        self.host = None
        self.port = None

    def finalize_options(self):
        if not self.host:
            print "[ERROR] Host is required, use --host=? to specify"
            sys.exit(1)
        if not self.port:
            print "[ERROR] Port is required, use --port=? to specify"
            sys.exit(1)
        if not self.port.isdigit():
            print "[ERROR] Invalid port"
            sys.exit(1)

    def run(self):
        import src.octohaven as octohaven
        octohaven.run(host=self.host, port=self.port)

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
        "start_server": StartServer
    }
)
