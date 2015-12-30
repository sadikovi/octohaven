#!/bin/bash
#################################################
### Octohaven app settings
#################################################
# Octohaven application host and port to service web pages and all, application will be available
# at "OCTOHAVEN_HOST:OCTOHAVEN_PORT"
export OCTOHAVEN_HOST="localhost"
export OCTOHAVEN_PORT="33900"

#################################################
### Octohaven Spark settings
#################################################
# Spark full master address to execute Spark jobs on a cluster
export OCTOHAVEN_SPARK_MASTER_ADDRESS="spark://jony-local.lan:7077"
# Spark full UI address (the one for job monitoring)
export OCTOHAVEN_SPARK_UI_ADDRESS="http://localhost:8080"
# Root folder as starting point to show .jar files, can have nested folders, this will show file
# catalog starting from this folder specified. Please try specifying some more precise than root "/"
export JAR_FOLDER="/Users/sadikovi/developer/octohaven/test/resources/filelist"
# Force new Spark master address, recommended to set this option.
# If variable is set (non-empty), it will update master address for a staled job with previous
# address to the valid address specified in configuration file before launching it, e.g. job was
# saved with address "spark://old.address:7077", address was updated to "spark://new.address:7077",
# job will be executed with new address, if configuration option is set.
export FORCE_SPARK_MASTER_ADDRESS="YES"

#################################################
### Docker Redis settings
#################################################
# if USE_DOCKER is non-empty, app will try pulling image with REDIS_VERSION, if it does not
# already exist, and spin up or start existing container REDIS_CONTAINER. It will assign host
# REDIS_HOST and map port to REDIS_PORT and will use REDIS_DB. Note that if USE_DOCKER is empty it
# will skip this section and will assume that Redis instance provided.
export USE_DOCKER="YES"
export REDIS_VERSION="3.0.0"
export REDIS_CONTAINER="octohaven-redis-container"

#################################################
### Redis settings
#################################################
# If Docker is used (USE_DOCKER is non-empty) Redis host will be assigned as container host
# (container IP address) automatically, and port will be bound to the REDIS_PORT specified. It is
# recommended not to change these settings, if USE_DOCKER is set.
# Otherwise, it will use REDIS_HOST and REDIS_PORT to connect to Redis instance running.
export REDIS_HOST="sandbox"
# Redis port
export REDIS_PORT="6379"
export REDIS_DB="11"
