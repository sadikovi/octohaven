#!/bin/bash

# overwrite Spark options, since we are not using it for tests
export OCTOHAVEN_SPARK_MASTER_ADDRESS="spark://test89e013856abc44bcb90982edb8b7ea46:9999"
export OCTOHAVEN_SPARK_UI_ADDRESS="http://test89e013856abc44bcb90982edb8b7ea46:9999"

export DOCKER_TEST_CONTAINER="octohaven-mysql-test-container"
export MYSQL_HOST="sandbox-test"
export MYSQL_PORT="3306"

# we cannot allow to use the same container for testing and running application.
if [ -n "$USE_DOCKER" ]; then
    if [ "$DOCKER_TEST_CONTAINER" == "$DOCKER_CONTAINER" ]; then
        echo "[ERROR] Test database should not be the same as actual database. "
        echo "Please set different DOCKER_TEST_CONTAINER"
        exit 1
    fi
fi

# overwrite container name for testing
DOCKER_CONTAINER="$DOCKER_TEST_CONTAINER"
