#!/bin/sh
# Octohaven app settings
export OCTOHAVEN_DEFAULT_PORT="33900"
# Octohaven Spark settings
export OCTOHAVEN_SPARK_MASTER_ADDRESS="spark://jony-local.local:7077"
export OCTOHAVEN_SPARK_UI_ADDRESS="http://localhost:8080"
# Redis settings
export REDIS_VERSION="3.0.0"
export REDIS_CONTAINER="octohaven-redis-container"
export REDIS_HOST="sandbox"
export REDIS_PORT="6379"
