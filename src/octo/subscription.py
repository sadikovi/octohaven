#!/usr/bin/env python

from threading import Lock
from types import StringType
from octolog import Octolog
from src.octo.utils import *

lock = Lock()

# Emitter class allows sending messages to events, that will be received by subscribers, if any.
# Event will be registerd automatically, once emitter calls `::broadcast()`, if it does not exist
# already
class Emitter(Octolog, object):
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def register(self, event):
        self.logger().debug("Registering event '%s'", event)
        self.dispatcher.addEvent(event)

    def broadcast(self, event, value):
        self.logger().debug("Broadcasting '%s' for event '%s'", value, event)
        self.dispatcher.addEvent(event)
        self.dispatcher.notify(event, value)

# Subscriber is instance that receives event. In order to receive messages for a particular event,
# call `::subscribe()`. Every subscriber, to process messages, must implement method `::receive()`
class Subscriber(Octolog, object):
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def subscribe(self, event, future=True):
        # "future" option allows us to register event without actually having it in the list
        if future:
            self.dispatcher.addEvent(event)
        self.dispatcher.addSubscriber(event, self)

    def unsubscribe(self, event):
        self.dispatcher.removeSubscriber(event, self)
        self.logger().debug("Unsubscribed from '%s'", event)

    # this method should be overwritten in subclasses to receive and process messages
    def receive(self, event, value):
        pass

# Dispatcher class that handles all communications between emitters and subscribers.
# We have also created global dispatcher that lives during the life of application.
class Dispatcher(Octolog, object):
    def __init__(self, name):
        self.events = {}
        self.name = str(name)

    @private
    def hasEvent(self, event):
        assertType(event, StringType)
        return event in self.events

    @private
    def hasEventOrFail(self, event):
        if not self.hasEvent(event):
            raise StandardError("No such event with name '%s' exists" % event)
        return True

    def clearAll(self):
        with lock:
            self.events = {}

    def addEvent(self, event):
        with lock:
            if self.hasEvent(event):
                self.logger().debug("Event '%s' has already been registerd", event)
                return
            self.events[event] = []
            self.logger().debug("%s: Added event '%s'", self.name, event)

    def removeEvent(self, event):
        with lock:
            self.hasEventOrFail(event)
            del self.events[event]
            self.logger().debug("%s: Removed event '%s'", self.name, event)

    def addSubscriber(self, event, obj):
        if not isinstance(obj, Subscriber):
            raise StandardError("Expected Subscriber, got " + str(type(obj)))
        with lock:
            self.hasEventOrFail(event)
            self.events[event].append(obj)
            self.logger().debug("%s: Added subscriber '%s'", self.name, str(obj.__class__))

    def removeSubscriber(self, event, obj):
        if not isinstance(obj, Subscriber):
            raise StandardError("Expected Subscriber, got " + str(type(obj)))
        with lock:
            self.hasEventOrFail(event)
            for sub in self.events[event]:
                if id(sub) == id(obj):
                    self.events[event].remove(sub)
                    self.logger().debug("%s: Removed subscriber '%s'", self.name,
                        str(sub.__class__))

    def notify(self, event, value):
        with lock:
            self.logger().debug("%s: Requested notification for event '%s' with value '%s'",
                self.name, event, value)
            # if we cannot find event, just ignore it
            if not self.hasEvent(event):
                return
            # notify every subscriber for an updated value
            subscribers = self.events[event]
            for sub in subscribers:
                sub.receive(event, value)

# Global dispatcher for the application
GLOBAL_DISPATCHER = Dispatcher("GLOBAL DISPATCHER")
