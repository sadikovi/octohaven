#!/usr/bin/env python

import unittest
import os
from paths import TEST_PATH
from src.filelist import FileList, File, Directory, JarFile

class FilelistTestSuite(unittest.TestCase):
    def setUp(self):
        self.root = os.path.join(TEST_PATH, "resources", "filelist", "root")

    def tearDown(self):
        pass

    def test_discover(self):
        root = Directory(self.root)
        files = FileList.discover(root)
        self.assertEqual(len(files), 3)
        for dr in files:
            self.assertEqual(dr.status, "DIR")
            self.assertEqual(os.path.isabs(dr.path), True)

    def test_complexDiscover(self):
        root = Directory(os.path.join(self.root, "test"))
        files = FileList.discover(root)
        self.assertEqual(len(files), 3)
        statuses = [dr.status for dr in files]
        self.assertEqual(sorted(statuses), ["DIR", "JAR", "JAR"])
        for dr in files:
            self.assertEqual(os.path.isabs(dr.path), True)

    def test_dropDiscover(self):
        root = Directory(os.path.join(self.root, "dev"))
        files = FileList.discover(root)
        self.assertEqual(len(files), 1)
        statuses = [dr.status for dr in files]
        self.assertEqual(sorted(statuses), ["JAR"])
        for dr in files:
            self.assertEqual(os.path.isabs(dr.path), True)

    def test_sort(self):
        root = Directory(self.root)
        files = FileList.discover(root)
        sort = FileList.sortFiles(files)
        self.assertEqual(len(sort), len(files))
        paths = [dr.path for dr in sort]
        expected = sorted([dr.path for dr in files])
        self.assertEqual(paths, expected)

    def test_mixedSort(self):
        root = Directory(os.path.join(self.root, "test"))
        files = FileList.discover(root)
        sort = FileList.sortFiles(files)
        self.assertEqual(len(sort), len(files))
        paths = [dr.path for dr in sort]
        expected = [os.path.join(root.path, "test1"), os.path.join(root.path, "atest.jar"),
            os.path.join(root.path, "btest.jar")]
        self.assertEqual(paths, expected)

    def test_lisAsDict(self):
        root = Directory(os.path.join(self.root, "test"))
        files = FileList.discover(root)
        sort = FileList.sortFiles(files)
        paths = FileList.listAsDict(sort)
        expected = [dr.toDict() for dr in sort]
        self.assertEqual(paths, expected)

# Load test suites
def _suites():
    return [
        FilelistTestSuite
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
