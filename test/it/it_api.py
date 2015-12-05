#!/usr/bin/env python

import unittest, json
from test.it.it_constants import Settings, Request

class it_ApiSuite(unittest.TestCase):
    def address(self):
        return "http://" + Settings.mp().get("host") + ":" + Settings.mp().get("port")

    def api(self, action):
        return "%s%s" % (self.address(), action)

    def test_sparkStatus(self):
        data = Request.get(self.api("/api/v1/spark/status"))
        obj = json.loads(data) if data and len(data) else None
        self.assertTrue(obj is not None)
        self.assertEqual(obj[u"status"], u"OK")
        self.assertEqual(obj[u"code"], 200)
        content = obj[u"content"]
        self.assertEqual(len(content), 3)
        status = content[u"status"]
        masterAddress = content[u"spark-master-address"]
        uiAddress = content[u"spark-ui-address"]
        self.assertTrue(status == -2)
        self.assertTrue(len(masterAddress) > 0)
        self.assertTrue(len(uiAddress) > 0)

# Load test suites
def _suites():
    return [
        it_ApiSuite
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
