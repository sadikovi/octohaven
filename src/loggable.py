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

import os, logging, logging.config
from internal import CONF_PATH, CONF_NAME

confFile = os.path.join(CONF_PATH, CONF_NAME)
# try loading configuration file, if not found, leave default
if os.path.exists(confFile):
    logging.config.fileConfig(confFile)
else:
    print "[WARN] Configuration is not found for: %s" % confFile

"""
Log messages available:
- ::debug(msg, *args, **kwargs)
- ::info(msg, *args, **kwargs)
- ::warning(msg, *args, **kwargs)
- ::error(msg, *args, **kwargs)
- ::critical(msg, *args, **kwargs)
- ::exception(msg, *args, **kwargs)
"""
class Loggable(object):
    def __init__(self, name=None):
        name = str(type(self).__name__ if not name else name)
        self.logger = logging.getLogger(name)
        self.logger.addHandler(logging.NullHandler())
