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

import os, unittest
from internal import ROOT_PATH
from src.fs import FileManager, BlockReader

class FileManagerTestSuite(unittest.TestCase):
    def setUp(self):
        self.root = os.path.join(ROOT_PATH, "test")
        self.resources = os.path.join(self.root, "resources")
        self.file = os.path.join(self.resources, "scheduler.txt")

    def tearDown(self):
        pass

    def test_create(self):
        manager = FileManager(self.root)
        self.assertEqual(manager.home, self.root)
        manager = FileManager("test")
        self.assertEqual(manager.home, self.root)
        with self.assertRaises(StandardError):
            FileManager(self.file)
        # test alias and extensions
        manager = FileManager(self.root, alias="/api/v1/finder")
        self.assertEqual(manager.alias, "/api/v1/finder")
        manager = FileManager(self.root, alias="/api/v1/finder", extensions=[".py", ".conf"])
        self.assertEqual(manager.alias, "/api/v1/finder")
        self.assertEqual(manager.extensions, [".py", ".conf"])

    def test_issubpath(self):
        manager = FileManager(self.root)
        self.assertEqual(manager.issubpath(self.file), True)
        self.assertEqual(manager.issubpath(ROOT_PATH), False)

    def test_ls(self):
        manager = FileManager(self.resources, alias="/home", extensions=[".jar"])
        a, b = manager.ls()
        self.assertEqual(a, [{"type": "dir", "isdir": True, "name": "home", "url": "/home",
            "realpath": self.resources}])
        self.assertEqual(b, [
            {"type": "dir", "isdir": True, "name": ".", "url": "/home", "realpath": self.resources},
            {"type": "dir", "isdir": True, "name": "filelist", "url": "/home/filelist",
                "realpath": os.path.join(self.resources, "filelist")},
            {"type": ".jar", "isdir": False, "name": "dummy.jar", "url": "/home/dummy.jar",
                "realpath": os.path.join(self.resources, "dummy.jar")}
        ])
        # testing different extensions
        manager = FileManager(self.resources, alias="/home", extensions=[".txt"])
        a, b = manager.ls()
        self.assertEqual(a, [{"type": "dir", "isdir": True, "name": "home", "url": "/home",
            "realpath": self.resources}])
        self.assertEqual(b, [
            {"type": "dir", "isdir": True, "name": ".", "url": "/home", "realpath": self.resources},
            {"type": "dir", "isdir": True, "name": "filelist", "url": "/home/filelist",
                "realpath": os.path.join(self.resources, "filelist")},
            {"type": ".txt", "isdir": False, "name": "empty.txt", "url": "/home/empty.txt",
                "realpath": os.path.join(self.resources, "empty.txt")},
            {"type": ".txt", "isdir": False, "name": "scheduler.txt", "url": "/home/scheduler.txt",
                "realpath": os.path.join(self.resources, "scheduler.txt")}
        ])

    def test_ls_traverse(self):
        manager = FileManager(self.resources, alias="/home", extensions=[".jar"])
        a, b = manager.ls("filelist", "dev")
        self.assertEqual(a, [
            {"type": "dir", "isdir": True, "name": "home", "url": "/home",
                "realpath": self.resources},
            {"type": "dir", "isdir": True, "name": "filelist", "url": "/home/filelist",
                "realpath": os.path.join(self.resources, "filelist")},
            {"type": "dir", "isdir": True, "name": "dev", "url": "/home/filelist/dev",
                "realpath": os.path.join(self.resources, "filelist", "dev")}
        ])
        self.assertEqual(b, [
            {"type": "dir", "isdir": True, "name": ".", "url": "/home/filelist/dev",
                "realpath": os.path.join(self.resources, "filelist", "dev")},
            {"type": "dir", "isdir": True, "name": "..", "url": "/home/filelist",
                "realpath": os.path.join(self.resources, "filelist")},
            {"type": ".jar", "isdir": False, "name": "dev-jar.jar",
                "url": "/home/filelist/dev/dev-jar.jar", "realpath": os.path.join(self.resources,
                    "filelist", "dev", "dev-jar.jar")}
        ])

    def test_ls_traverse_without_nodes(self):
        # only ".." is included
        manager = FileManager(self.resources, alias="/home", extensions=[".jar"], showOneNode=False)
        a, b = manager.ls("filelist", "dev")
        self.assertEqual(a, [
            {"type": "dir", "isdir": True, "name": "home", "url": "/home",
                "realpath": self.resources},
            {"type": "dir", "isdir": True, "name": "filelist", "url": "/home/filelist",
                "realpath": os.path.join(self.resources, "filelist")},
            {"type": "dir", "isdir": True, "name": "dev", "url": "/home/filelist/dev",
                "realpath": os.path.join(self.resources, "filelist", "dev")}
        ])
        self.assertEqual(b, [
            {"type": "dir", "isdir": True, "name": "..", "url": "/home/filelist",
                "realpath": os.path.join(self.resources, "filelist")},
            {"type": ".jar", "isdir": False, "name": "dev-jar.jar",
                "url": "/home/filelist/dev/dev-jar.jar", "realpath": os.path.join(self.resources,
                    "filelist", "dev", "dev-jar.jar")}
        ])

        # none of "." and ".." are included
        manager = FileManager(self.resources, alias="/home", extensions=[".jar"],
            showOneNode=False, showTwoNode=False)
        a, b = manager.ls("filelist", "dev")
        self.assertEqual(b, [
            {"type": ".jar", "isdir": False, "name": "dev-jar.jar",
                "url": "/home/filelist/dev/dev-jar.jar", "realpath": os.path.join(self.resources,
                    "filelist", "dev", "dev-jar.jar")}
        ])

# File reading API
class BlockReaderTestSuite(unittest.TestCase):
    def setUp(self):
        self.file = os.path.join(ROOT_PATH, "test", "resources", "scheduler.txt")
        self.emptyFile = os.path.join(ROOT_PATH, "test", "resources", "empty.txt")

    def tearDown(self):
        pass

    def test_endOfFile(self):
        manager = BlockReader()
        with open(self.file) as f:
            self.assertEqual(manager.endOfFile(f), 2249)

    def test_startOfFile(self):
        manager = BlockReader()
        with open(self.file) as f:
            self.assertEqual(manager.startOfFile(f), 0)

    def test_validation(self):
        manager = BlockReader()
        # file validation
        with self.assertRaises(StandardError):
            manager.validateFile(None)
        with open(self.file) as f:
            self.assertEqual(manager.validateFile(f), f)
        # page validation
        with self.assertRaises(StandardError):
            manager.validatePage(None)
        with self.assertRaises(StandardError):
            manager.validatePage(-1)
        with self.assertRaises(StandardError):
            manager.validatePage(-1.0)
        self.assertEqual(manager.validatePage(10), 10)
        # position validation
        with self.assertRaises(StandardError):
            manager.validatePosition(None)
        with self.assertRaises(StandardError):
            manager.validatePosition(-1)
        with self.assertRaises(StandardError):
            manager.validatePosition(-1.0)
        self.assertEqual(manager.validatePosition(100), 100)

    def test_numPages(self):
        manager = BlockReader()
        with open(self.file) as f:
            self.assertEqual(manager.numPages(f, chunk=1000), 3)
            self.assertEqual(manager.numPages(f, chunk=500), 5)
            self.assertEqual(manager.numPages(f, chunk=2249), 1)

    def test_read(self):
        manager = BlockReader()
        with open(self.file) as f:
            with self.assertRaises(StandardError):
                manager.read(f, -1, 100)
            with self.assertRaises(StandardError):
                manager.read(f, 100, 50)
            block = manager.read(f, 100, 150)
            self.assertEqual(block, "t or add functionality\n- Some important configurat")

    def test_readFromPosition(self):
        manager = BlockReader()
        with self.assertRaises(StandardError):
            manager.readFromPosition(None, 100, offset=200)
        with open(self.file) as f:
            block = manager.readFromPosition(f, -1, offset=10)
            self.assertEqual(block, "Main poin")
            block = manager.readFromPosition(f, 500, offset=100)
            self.assertEqual(block, "ules:\n- Fetching jobs that are ready to be run (1)\n- " +
                "Checking whether we can execute job (2)\n- Actua")
            block = manager.readFromPosition(f, 500, offset=-100)
            self.assertEqual(block, "echanism\nthat includes tasks listed above.\nTechnically " +
                "scheduler is more of combination of three mod")

    def test_readFromStart(self):
        manager = BlockReader()
        with open(self.file) as f:
            block = manager.readFromStart(f, 3, chunk=100, offset=0)
            self.assertEqual(block, "d to config.sh\n\nThe whole job of scheduler is checking " +
                "whether cluster is available and running jobs")
            block = manager.readFromStart(f, 3, chunk=100, offset=100)
            self.assertEqual(block, "- Some important configuration options should be separated, " +
                "and possibly moved to config.sh\n\nThe whole job of scheduler is checking " +
                "whether cluster is available and running jobs, if it is,")

    def test_readFromEnd(self):
        manager = BlockReader()
        with open(self.file) as f:
            block = manager.readFromEnd(f, 2, chunk=100, offset=0)
            self.assertEqual(block, "g a link.\nWe maintain pool of links. Constantly we check " +
                "status of those processes. Once process is ")
            block = manager.readFromEnd(f, 2, chunk=100, offset=100)
            self.assertEqual(block, "is all good, we execute command. Tracker gets process id " +
                "and maps to the job id by creating a link.\nWe maintain pool of links. " +
                "Constantly we check status of those processes. Once process is finished")

    def crop(self):
        manager = BlockReader()
        with open(self.file) as f:
            block = manager.crop(f, 100, 50)
            self.assertEqual(block, "t or add functionality")
            block = manager.crop(f, 100, -50)
            self.assertEqual(block, "- Should be very easy to extend i")
            block = manager.crop(f, 100, 100)
            self.assertEqual(block, "t or add functionality")

    # issue 25:
    def test_validatePageWhenReading(self):
        manager = BlockReader()
        with open(self.file) as f:
            numPages = manager.numPages(f, chunk=100)
            self.assertEqual(numPages, 23)
            # test exceeded number of pages
            with self.assertRaises(StandardError):
                manager.readFromStart(f, numPages + 1, chunk=100, offset=0)
            with self.assertRaises(StandardError):
                manager.readFromEnd(f, numPages + 1, chunk=100, offset=0)
            # test negative page number
            with self.assertRaises(StandardError):
                manager.readFromStart(f, 0, chunk=100, offset=0)
            with self.assertRaises(StandardError):
                manager.readFromEnd(f, 0, chunk=100, offset=0)
            # this should be okay
            manager.readFromStart(f, numPages, chunk=100, offset=0)
            manager.readFromEnd(f, numPages, chunk=100, offset=0)

    def test_minNumPages(self):
        # number of pages should be at least 1, so empty file will say that it has 1 page, which is
        # empty
        manager = BlockReader()
        with open(self.emptyFile) as f:
            numPages = manager.numPages(f, chunk=200)
            self.assertEqual(numPages, 1)
        with open(self.file) as f:
            numPages = manager.numPages(f, chunk=200)
            self.assertEqual(numPages, 12)

# Load test suites
def _suites():
    return [
        FileManagerTestSuite,
        BlockReaderTestSuite
    ]

# Load tests
def loadSuites():
    # global test suite for this module
    gsuite = unittest.TestSuite()
    for suite in _suites():
        gsuite.addTest(unittest.TestLoader().loadTestsFromTestCase(suite))
    return gsuite

if __name__ == '__main__':
    suite = loadSuites()
    print ""
    print "### Running tests ###"
    print "-" * 70
    unittest.TextTestRunner(verbosity=2).run(suite)
