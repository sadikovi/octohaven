#!/bin/sh

# find python to run server
export WHICH_PYTHON=$(which python)
if [ -z "$WHICH_PYTHON" ]; then
    echo "[ERROR] Python is not found. Cannot work without python"
    exit 1
fi

# enforce Python 2.7.x
PYTHON_VERSION=$($WHICH_PYTHON -c 'import sys; print ".".join([str(x) for x in sys.version_info[0:2]])')
if [ "$PYTHON_VERSION" != "2.7" ]; then
    echo "[ERROR] Python 2.7 required, found Python $PYTHON_VERSION"
    exit 1
fi
