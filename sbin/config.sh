#!/bin/bash
# Octohaven app settings
## Octohaven application host and port to service web pages and all, application will be available
## at "OCTOHAVEN_HOST:OCTOHAVEN_PORT"
export OCTOHAVEN_HOST="localhost"
export OCTOHAVEN_PORT="33900"
# Octohaven Spark settings
# Spark full master address to execute Spark jobs on a cluster
export OCTOHAVEN_SPARK_MASTER_ADDRESS="spark://jony-local.local:7077"
# Spark full UI address (the one for job monitoring)
export OCTOHAVEN_SPARK_UI_ADDRESS="http://localhost:8080"
# Spark full UI address for running job (usually, http://localhost:4040, this will be used to
# update information from Spark UI)
export OCTOHAVEN_SPARK_UI_RUN_ADDRESS="http://localhost:4040"
# Root path for .jar files, can have nested folders, this will show file catalog starting from
# this folder specified
export JAR_FOLDER="/Users/sadikovi/developer/octohaven/test/resources/filelist"
# Docker Redis settings
## if USE_DOCKER is non-empty, app will try pulling image with REDIS_VERSION, if it does not
## already exist, and spin up or start existing container REDIS_CONTAINER. Otherwise, it will
## ignore Docker and will try connecting to the Redis settings section specified below.
export USE_DOCKER="YES"
export REDIS_VERSION="3.0.0"
export REDIS_CONTAINER="octohaven-redis-container"
# Redis settings
## If Docker is used (USE_DOCKER is non-empty) Redis host will be assigned as container host
## (Docker ip address) automatically, and port will be bound to the REDIS_PORT specified.
## Otherwise, it will use REDIS_HOST and REDIS_PORT to connect to Redis instance running.
export REDIS_HOST="sandbox"
# Redis port
export REDIS_PORT="6379"
export REDIS_DB="11"
