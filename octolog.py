#!/usr/bin/env python

import paths, os, re
import logging
import logging.config

confFile = os.path.join(paths.SBIN_PATH, "log.conf")
# try loading configuration file, if not found, leave default
if os.path.exists(confFile):
    # configure logger
    logging.config.fileConfig(confFile)
else:
    print "[WARN] Configuration is not found for: %s" % confFile

def _logger(name):
    logger = logging.getLogger(name)
    logger.addHandler(logging.NullHandler())
    return logger

"""
Log messages available:
- ::debug(msg, *args, **kwargs)
- ::info(msg, *args, **kwargs)
- ::warning(msg, *args, **kwargs)
- ::error(msg, *args, **kwargs)
- ::critical(msg, *args, **kwargs)
- ::exception(msg, *args, **kwargs)
"""
class Octolog(object):
    def logger(self):
        name = str(type(self).__name__)
        return _logger(name)
