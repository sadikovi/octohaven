#!/usr/bin/env python

import os
import sys

# system paths
## file must be in project root
ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
LIB_PATH = os.path.join(ROOT_PATH, 'lib')
SRC_PATH = os.path.join(ROOT_PATH, 'src')
TEST_PATH = os.path.join(ROOT_PATH, 'test')
## set system path to the root directory
sys.path.append(ROOT_PATH)
## set system path to the lib directory
sys.path.append(LIB_PATH)
## set system path to the src directory
sys.path.append(SRC_PATH)
## set system path to the test directory
sys.path.append(TEST_PATH)
