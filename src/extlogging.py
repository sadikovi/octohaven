#!/usr/bin/env python

import os, logging, logging.config
from info import CONF_PATH

confFile = os.path.join(CONF_PATH, "log.conf")
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
    def __init__(self):
        name = str(type(self).__name__)
        self.logger = logging.getLogger(name)
        self.logger.addHandler(logging.NullHandler())
