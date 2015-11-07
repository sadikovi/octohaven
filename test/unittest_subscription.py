#!/usr/bin/env python

import unittest
from src.subscription import Dispatcher, Emitter, Subscriber

TEST_DISPATCHER = Dispatcher("TEST DISPATCHER")

class EmitterTestSuite(unittest.TestCase):
    def init(self, name):
        emitter = Emitter(TEST_DISPATCHER)
        emitter.register(name)
        self.assertEqual(name in emitter.dispatcher.events, True)

    def test_init(self):
        self.init("listen-to-event")
        # try inserting object instead of string
        with self.assertRaises(StandardError):
            self.init({})

class SubscriberTestSuite(unittest.TestCase):
    def test_init(self):
        a = Subscriber(TEST_DISPATCHER)
        self.assertEqual(a.dispatcher is TEST_DISPATCHER, True)

# creating test classes for subscription
class A(Emitter, object):
    def __init__(self):
        Emitter.__init__(self, TEST_DISPATCHER)

class B(Subscriber, object):
    def __init__(self):
        self.value = None
        Subscriber.__init__(self, TEST_DISPATCHER)

    def receive(self, event, value):
        if event == "test-event" and value:
            self.value = value

class DispatcherTestSuite(unittest.TestCase):
    def setUp(self):
        self.a = A()
        self.a.register("test-event")
        self.b = B()
        self.b.subscribe("test-event")

    def tearDown(self):
        self.a = None
        self.b = None
        TEST_DISPATCHER.clearAll()

    def test_addEvent(self):
        TEST_DISPATCHER.addEvent("another-test-event")
        self.assertEqual(len(TEST_DISPATCHER.events), 2)

    def test_removeEvent(self):
        with self.assertRaises(StandardError):
            TEST_DISPATCHER.removeEvent("unknown-event")
        TEST_DISPATCHER.removeEvent("test-event")

    def test_addSubscriber(self):
        with self.assertRaises(StandardError):
            TEST_DISPATCHER.addSubscriber("test-event", None)
        TEST_DISPATCHER.addSubscriber("test-event", Subscriber(TEST_DISPATCHER))
        self.assertEqual(len(TEST_DISPATCHER.events["test-event"]), 2)

    def test_removeSubcriber(self):
        with self.assertRaises(StandardError):
            TEST_DISPATCHER.removeSubscriber("test-event", None)
        TEST_DISPATCHER.removeSubscriber("test-event", self.b)
        self.assertEqual(len(TEST_DISPATCHER.events["test-event"]), 0)

    def test_subscribe(self):
        # this should not throw exception
        self.a.broadcast("test-event", False)
        # this should update value in `b`
        self.a.broadcast("test-event", True)
        self.assertEqual(self.b.value, True)
        # should not update value, since we unsubscribed
        self.b.unsubscribe("test-event")
        self.a.broadcast("test-event", "str")
        self.assertEqual(self.b.value, True)
        # check string value
        self.b.subscribe("test-event")
        self.a.broadcast("test-event", "True")
        self.assertEqual(self.b.value, "True")

# Load test suites
def _suites():
    return [
        DispatcherTestSuite,
        EmitterTestSuite,
        SubscriberTestSuite
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
