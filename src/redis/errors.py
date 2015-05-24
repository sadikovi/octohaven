#!/usr/bin/env python

class CoreError(StandardError):
    def __init__(self, message):
        self._msg = message
        super(CoreError, self).__init__(self._msg)

class ConnectorError(StandardError):
    def __init__(self, message):
        self._msg = message
        super(ConnectorError, self).__init__(self._msg)
