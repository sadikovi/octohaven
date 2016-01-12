#!/usr/bin/env python

import os, unittest
from paths import TEST_PATH
from src.octo.filemanager import FileManager, SEP, ROOT, File, Directory, JarFile

class FileManagerTestSuite(unittest.TestCase):
    def setUp(self):
        self.root = os.path.join(TEST_PATH, "resources", "filelist")
        self.file = os.path.join(TEST_PATH, "resources", "scheduler.txt")
        self.emptyFile = os.path.join(TEST_PATH, "resources", "empty.txt")

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

    # File reading API
    def test_endOfFile(self):
        manager = FileManager(self.root)
        with open(self.file) as f:
            self.assertEqual(manager.endOfFile(f), 2249)

    def test_startOfFile(self):
        manager = FileManager(self.root)
        with open(self.file) as f:
            self.assertEqual(manager.startOfFile(f), 0)

    def test_validation(self):
        manager = FileManager(self.root)
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
        manager = FileManager(self.root)
        with open(self.file) as f:
            self.assertEqual(manager.numPages(f, chunk=1000), 3)
            self.assertEqual(manager.numPages(f, chunk=500), 5)
            self.assertEqual(manager.numPages(f, chunk=2249), 1)

    def test_read(self):
        manager = FileManager(self.root)
        with open(self.file) as f:
            with self.assertRaises(StandardError):
                manager.read(f, -1, 100)
            with self.assertRaises(StandardError):
                manager.read(f, 100, 50)
            block = manager.read(f, 100, 150)
            self.assertEqual(block, "t or add functionality\n- Some important configurat")

    def test_readFromPosition(self):
        manager = FileManager(self.root)
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
        manager = FileManager(self.root)
        with open(self.file) as f:
            block = manager.readFromStart(f, 3, chunk=100, offset=0)
            self.assertEqual(block, "d to config.sh\n\nThe whole job of scheduler is checking " +
                "whether cluster is available and running jobs")
            block = manager.readFromStart(f, 3, chunk=100, offset=100)
            self.assertEqual(block, "- Some important configuration options should be separated, " +
                "and possibly moved to config.sh\n\nThe whole job of scheduler is checking " +
                "whether cluster is available and running jobs, if it is,")

    def test_readFromEnd(self):
        manager = FileManager(self.root)
        with open(self.file) as f:
            block = manager.readFromEnd(f, 2, chunk=100, offset=0)
            self.assertEqual(block, "g a link.\nWe maintain pool of links. Constantly we check " +
                "status of those processes. Once process is ")
            block = manager.readFromEnd(f, 2, chunk=100, offset=100)
            self.assertEqual(block, "is all good, we execute command. Tracker gets process id " +
                "and maps to the job id by creating a link.\nWe maintain pool of links. " +
                "Constantly we check status of those processes. Once process is finished")

    def crop(self):
        manager = FileManager(self.root)
        with open(self.file) as f:
            block = manager.crop(f, 100, 50)
            self.assertEqual(block, "t or add functionality")
            block = manager.crop(f, 100, -50)
            self.assertEqual(block, "- Should be very easy to extend i")
            block = manager.crop(f, 100, 100)
            self.assertEqual(block, "t or add functionality")

    # issue 25:
    def test_validatePageWhenReading(self):
        manager = FileManager(self.root)
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
        manager = FileManager(self.root)
        with open(self.emptyFile) as f:
            numPages = manager.numPages(f, chunk=200)
            self.assertEqual(numPages, 1)
        with open(self.file) as f:
            numPages = manager.numPages(f, chunk=200)
            self.assertEqual(numPages, 12)

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
