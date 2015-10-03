#!/bin/sh
# Octohaven app settings
# Octohaven application port to service web pages and all
export OCTOHAVEN_PORT="33900"
# Octohaven Spark settings
# Spark full master address to execute Spark jobs on a cluster
export OCTOHAVEN_SPARK_MASTER_ADDRESS="spark://jony-local.local:7077"
# Spark full UI address (the one for job monitoring)
export OCTOHAVEN_SPARK_UI_ADDRESS="http://localhost:8080"
# Docker Redis settings
# if USE_DOCKER is non-empty, app will try pulling image with REDIS_VERSION, if it does not already
# exist, and spin up or start existing container REDIS_CONTAINER. Otherwise, it will ignore Docker
# and will try connecting to the REDIS_HOST specified below.
export USE_DOCKER="YES"
export REDIS_VERSION="3.0.0"
export REDIS_CONTAINER="octohaven-redis-container"
# Redis settings
# Redis host will be set to Docker ip address automatically, if USE_DOCKER is non-empty. Otherwise,
# it will try connecting to the host specified
export REDIS_HOST="sandbox"
export REDIS_PORT="6379"
export REDIS_DB="11"
