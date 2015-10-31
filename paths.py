#!/usr/bin/env python

import os
import sys

# system paths
## file must be in project root
ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
LIB_PATH = os.path.join(ROOT_PATH, 'lib')
SBIN_PATH = os.path.join(ROOT_PATH, 'sbin')
SRC_PATH = os.path.join(ROOT_PATH, 'src')
SERV_PATH = os.path.join(ROOT_PATH, 'service')
TEST_PATH = os.path.join(ROOT_PATH, 'test')
LOGS_PATH = os.path.join(ROOT_PATH, 'apache', 'spark', 'logs')
## set system path to the root directory
sys.path.append(ROOT_PATH)
## set system path to the lib directory
sys.path.append(LIB_PATH)
## set system path to the sbin directory (for conf files)
sys.path.append(SBIN_PATH)
## set system path to the src directory
sys.path.append(SRC_PATH)
## set system path to the service directory
sys.path.append(SERV_PATH)
## set system path to the test directory
sys.path.append(TEST_PATH)
## set system path to the Apache Spark logs folder (just for reference)
sys.path.append(LOGS_PATH)

# In order to create folder for Spark logs for each job, we create folders recursively and
# check path on existence
if not os.path.exists(LOGS_PATH):
    os.makedirs(LOGS_PATH)
# also check that we can write into that folder
if not os.access(LOGS_PATH, os.W_OK):
    raise IOError("No writing permissions for logs directory %s" % LOGS_PATH)
