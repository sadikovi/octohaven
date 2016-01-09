#!/bin/bash
#################################################
# Octohaven app settings
#################################################
# Octohaven application host and port to service web pages and all, application will be available
# at "OCTOHAVEN_HOST:OCTOHAVEN_PORT"
export OCTOHAVEN_HOST="localhost"
export OCTOHAVEN_PORT="33900"

#################################################
# Octohaven Spark settings
#################################################
# Spark full master address to execute Spark jobs on a cluster
export OCTOHAVEN_SPARK_MASTER_ADDRESS="spark://jony-local.lan:7077"
# Spark full UI address (the one for job monitoring)
export OCTOHAVEN_SPARK_UI_ADDRESS="http://localhost:8080"
# Root folder as starting point to show .jar files, can have nested folders, this will show file
# catalog starting from this folder specified. It takes some time to build directory, so please be
# more specific rather than specifying root folder
export JAR_FOLDER="/Users/sadikovi/developer/octohaven/test/resources/filelist"

#################################################
# Docker settings
#################################################
# if USE_DOCKER is non-empty, application will start setting up docker container DOCKER_CONTAINER,
# if it does not already exist. In this case MySQL settings will be automatically bound to the
# settings specified below, including when running using docker-machine. Note that operations
# sometimes include cleanup/removal of container, therefore do not specify other existing container
export USE_DOCKER="YES"
export DOCKER_CONTAINER="octohaven-mysql-container"

#################################################
# MySQL settings
#################################################
# If Docker is used (USE_DOCKER is non-empty) settings will be mapped to container settings
# Otherwise, it will use settings to connect to MySQL instance directly.
export MYSQL_HOST="sandbox"
export MYSQL_PORT="3306"
export MYSQL_USER="user"
export MYSQL_PASSWORD="12345"
export MYSQL_DATABASE="octohaven"
