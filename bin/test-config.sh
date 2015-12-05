#!/bin/bash

# Load test configuration, e.g. test Redis db and etc.
export REDIS_TEST_DB="15"
# make sure that we are setting Redis test DB
# we cannot allow to use the same DB for testing and running app, because some tests flush DB.
if [ "$REDIS_TEST_DB" == "$REDIS_DB" ]; then
    echo "[ERROR] Test DB should not match actual DB. Please set different REDIS_TEST_DB"
    exit 1
else
    REDIS_DB="$REDIS_TEST_DB"
fi

# overwrite Spark options, since we are not using it for tests
export OCTOHAVEN_SPARK_MASTER_ADDRESS="spark://test89e013856abc44bcb90982edb8b7ea46:9999"
export OCTOHAVEN_SPARK_UI_ADDRESS="http://test89e013856abc44bcb90982edb8b7ea46:9999"
