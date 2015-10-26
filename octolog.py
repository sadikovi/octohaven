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

class Octolog(object):
    def logger(self):
        name = str(self.__class__)
        groups = re.match(r"^<class\s*'([\.\w-]+)'\s*>$", name)
        if groups:
            name = groups.group(1)
        return _logger(name)
