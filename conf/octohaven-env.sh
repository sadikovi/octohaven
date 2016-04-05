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
export OCTOHAVEN_SPARK_MASTER_ADDRESS="spark://jony-local.local:7077"
# Spark full UI address (the one for job monitoring)
export OCTOHAVEN_SPARK_UI_ADDRESS="http://localhost:8080"
# Root folder as starting point to show .jar files, can have nested folders, this will show file
# catalog starting from this folder specified. It takes some time to build directory, so please be
# more specific rather than specifying root folder, e.g. /home
export JAR_FOLDER="test/resources/filelist"
# Working directory (optional). Working directory is a directory where application stores logs for
# each job and metadata, by default it is 'work/' in current directory. Note that this directory
# must have read and write access by the application
# export WORKING_DIR="./work"
#
# Number of slots, defines number of jobs allowed to be launched or running at the same time. This
# includes all jobs launched by application as well as Spark cluster. Default is 1, application will
# launch only one job at a time
# export NUM_SLOTS=1

#################################################
# MySQL settings
#################################################
# If used with USE_DOCKER, container will be created with host, port, database and credentials
# specified below. Otherwise application will try connecting to the settings directly
export MYSQL_HOST="sandbox"
export MYSQL_PORT="3306"
export MYSQL_USER="user"
export MYSQL_PASSWORD="12345"
export MYSQL_DATABASE="octohaven"

#################################################
# Docker
#################################################
# This option indicates if you want MySQL container to be launched by docker as part of the
# start-up process. Application will download image and launch container automatically, and stop it
# as part of shutdown process. If set "NO" or unset, application will assume that MySQL is provided
# externally, and will use settings above to connect to it.
export USE_DOCKER="YES"
# Name of the container to launch (takes effect only if USE_DOCKER is "YES")
export OCTOHAVEN_CONTAINER_NAME="octohaven-mysql-container"
