#!/bin/bash
# Octohaven app settings
## Octohaven application port to service web pages and all, application will be available
## at "localhost:OCTOHAVEN_PORT"
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
## ignore Docker and will try connecting to the REDIS_HOST specified below.
export USE_DOCKER="YES"
export REDIS_VERSION="3.0.0"
export REDIS_CONTAINER="octohaven-redis-container"
# Redis settings
## Redis host will be set to Docker ip address automatically, if USE_DOCKER is non-empty.
## Otherwise, it will try connecting to the host specified
export REDIS_HOST="sandbox"
# Redis port
export REDIS_PORT="6379"
export REDIS_DB="11"
