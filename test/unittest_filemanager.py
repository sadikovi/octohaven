#!/usr/bin/env python

import unittest
import os
from paths import TEST_PATH
from src.filemanager import FileManager, SEP, ROOT, File, Directory, JarFile

class FileManagerTestSuite(unittest.TestCase):
    def setUp(self):
        self.root = os.path.join(TEST_PATH, "resources", "filelist")

    def tearDown(self):
        pass

    def test_create(self):
        manager = FileManager(self.root)
        self.assertEqual(manager.root, self.root)
        with self.assertRaises(StandardError):
            FileManager("current/dir")

    def test_checkPath(self):
        manager = FileManager(self.root)
        paths = ["/absolute/path"]
        for path in paths:
            self.assertEqual(manager.checkPath(path), True)
        paths = ["local/path", "/path*/with?/parts;"]
        for path in paths:
            self.assertEqual(manager.checkPath(path), False)

    def test_checkDirectory(self):
        manager = FileManager(self.root)
        parts = ["part1", "part.2", "part-3", "part_4"]
        for part in parts:
            self.assertEqual(manager.checkDirectory(part), True)
        parts = ["part;1", ".", "..", "/", "part!"]
        for part in parts:
            self.assertEqual(manager.checkDirectory(part), False)

    def test_path(self):
        manager = FileManager(self.root)
        directory = SEP + "path" + SEP + "to" + SEP + "folder"
        with self.assertRaises(StandardError):
            manager.path(directory)
        directory = ROOT + SEP + "path*" + SEP + ";" + SEP + "folder"
        with self.assertRaises(StandardError):
            manager.path(directory)
        directory = ROOT + SEP + "path" + SEP + "to" + SEP + "folder"
        arr = manager.path(directory)
        self.assertEqual(arr, [ROOT, "path", "to", "folder"])

    def test_list(self):
        manager = FileManager(self.root)
        directory = ROOT
        files = manager.list(directory, sort=False, asdict=False)
        self.assertEqual(len(files), 3)
        for dr in files:
            self.assertEqual(dr.tp, "DIR")
            self.assertEqual(dr.path, ROOT + SEP + dr.name)

    def test_complexList(self):
        manager = FileManager(self.root)
        directory = ROOT + SEP + "test"
        files = manager.list(directory, sort=False, asdict=False)
        self.assertEqual(len(files), 3)
        statuses = [dr.tp for dr in files]
        self.assertEqual(sorted(statuses), ["DIR", "JAR", "JAR"])
        for dr in files:
            self.assertEqual(dr.path, directory + SEP + dr.name)

    def test_dropList(self):
        manager = FileManager(self.root)
        directory = ROOT + SEP + "dev"
        files = manager.list(directory, sort=False, asdict=False)
        self.assertEqual(len(files), 1)
        statuses = [dr.tp for dr in files]
        self.assertEqual(sorted(statuses), ["JAR"])
        for dr in files:
            self.assertEqual(dr.path, directory + SEP + dr.name)

    def test_sort(self):
        manager = FileManager(self.root)
        directory = ROOT
        files = manager.list(directory, sort=True, asdict=False)
        paths = [dr.path for dr in files]
        expected = sorted([dr.path for dr in files])
        self.assertEqual(paths, expected)

    def test_mixedSort(self):
        manager = FileManager(self.root)
        directory = ROOT + SEP + "test"
        files = manager.list(directory, sort=True, asdict=False)
        paths = [dr.path for dr in files]
        expected = [directory + SEP + "test1", directory + SEP + "atest.jar",
            directory + SEP + "btest.jar"]
        self.assertEqual(paths, expected)

    def test_listAsDict(self):
        manager = FileManager(self.root)
        directory = ROOT + SEP + "test"
        files = manager.list(directory, sort=False, asdict=True)
        expected = [dr.toDict() for dr in manager.list(directory, sort=False, asdict=False)]
        self.assertEqual(files, expected)

    def test_breadcrumbs(self):
        manager = FileManager(self.root)
        directory = ROOT + SEP + "test" + SEP + "test1"
        brd = manager.breadcrumbs(directory, asdict=False)
        self.assertEqual([x.name for x in brd], [ROOT, "test", "test1"])
        self.assertEqual([x.path for x in brd], [ROOT, ROOT + SEP + "test",
            ROOT + SEP + "test" + SEP + "test1"])

    def test_emptyBreadcrumbs(self):
        manager = FileManager(self.root)
        brd = manager.breadcrumbs("", asdict=True)
        expected = manager.breadcrumbs(ROOT, asdict=True)
        self.assertEqual(brd, expected)

    def test_emptyList(self):
        manager = FileManager(self.root)
        files = manager.list("", sort=True, asdict=True)
        expected = manager.list(ROOT, sort=True, asdict=True)
        self.assertEqual(files, expected)

    def test_resolveRelativePath(self):
        manager = FileManager(self.root)
        directory = ROOT + SEP + "test"
        obj = manager.list(directory, sort=False, asdict=False)[0]
        abspath = manager.resolveRelativePath(obj.path)
        self.assertEqual(abspath, os.path.join(self.root, "test", obj.name))
        # test failure cases
        with self.assertRaises(StandardError):
            manager.resolveRelativePath("")
        with self.assertRaises(StandardError):
            manager.resolveRelativePath("root" + SEP + "another")

# Load test suites
def _suites():
    return [
        FileManagerTestSuite
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
