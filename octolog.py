#!/usr/bin/env python

import paths, os
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

class Octolog(object):
    def logger(self):
        return _logger(str(self.__class__))
