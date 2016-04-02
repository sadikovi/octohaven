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

import signal

class GracefulShutdown:
    def __init__(self):
        self.stop_now = False
        self.callback = None
        # Register exit on SIGINT, SIGTERM
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)

    def exit(self, signum, frame):
        self.stop_now = True
        if self.callback:
            self.callback()

    def registerCallback(self, callback):
        self.callback = callback
