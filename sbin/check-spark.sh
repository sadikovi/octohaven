#!/bin/bash

# figure out project directory
sbin="`dirname "$0"`"
ROOT_DIR="`cd "$sbin/../"; pwd`"

# check SPARK_HOME, if available. If not, raise warning
if [ -z "$SPARK_HOME" ]; then
    echo "[WARN] SPARK_HOME is not set"
fi

# check spark-submit, fail if we cannot find it
export WHICH_SPARK_SUBMIT=$(which spark-submit)
if [ -z "$WHICH_SPARK_SUBMIT" ]; then
    echo "[ERROR] Cannot find spark-submit. Check that Spark is installed correctly"
    exit 1
fi
