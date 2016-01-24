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
# MySQL settings
#################################################
export MYSQL_HOST="sandbox"
export MYSQL_PORT="3306"
export MYSQL_USER="user"
export MYSQL_PASSWORD="12345"
export MYSQL_DATABASE="octohaven"
