#!/bin/bash

# figure out project directory
sbin="`dirname "$0"`"
ROOT_DIR="`cd "$sbin/../"; pwd`"

# load default variables (Octohaven and Redis settings)
. "$ROOT_DIR/sbin/config.sh"

# check dependencies (python is always checked)
. "$ROOT_DIR/sbin/check-python.sh"

# check if we are using Docker
if [ -n "$USE_DOCKER" ]; then
    . "$ROOT_DIR/sbin/check-docker.sh"

    # check if container exists and running
    DOCKER_REDIS_EXISTS=$(docker ps -a | grep -e "$REDIS_CONTAINER$")
    DOCKER_REDIS_RUNNING=$(docker ps | grep -e "$REDIS_CONTAINER$")
    if [ -z "$DOCKER_REDIS_RUNNING" ]; then
        if [ -z "$DOCKER_REDIS_EXISTS" ]; then
            # run new container, as no container can be found
            echo "[INFO] Running new Redis container..."
            eval "$WHICH_DOCKER run -h $REDIS_HOST -p $REDIS_PORT:6379 --name $REDIS_CONTAINER -d redis:$REDIS_VERSION"
        else
            # start stopped container
            echo "[INFO] Starting up Redis container..."
            eval "$WHICH_DOCKER start $REDIS_CONTAINER"
        fi
    else
        echo "[INFO] Redis is already running"
    fi
    # if we use Docker we have to reevaluate Redis host, as it will be VM IP in case of boot2docker
    # or localhost on Linux
    if [ -n "$WHICH_DOCKER_MACHINE" ]; then
        ACTIVE_VM=$($WHICH_DOCKER_MACHINE active)
        REDIS_HOST=$($WHICH_DOCKER_MACHINE ip $ACTIVE_VM)
    else
        REDIS_HOST="localhost"
    fi
fi

# check that jar folder exists
if [ ! -d "$JAR_FOLDER" ]; then
    echo "[ERROR] $JAR_FOLDER does not exist"
    exit 1
fi

# start serving
eval "$WHICH_PYTHON $ROOT_DIR/run_service.py \
    --port=$OCTOHAVEN_PORT \
    --spark-ui-address=$OCTOHAVEN_SPARK_UI_ADDRESS \
    --spark-ui-run-address=$OCTOHAVEN_SPARK_UI_RUN_ADDRESS \
    --spark-master-address=$OCTOHAVEN_SPARK_MASTER_ADDRESS \
    --redis-host=$REDIS_HOST \
    --redis-port=$REDIS_PORT \
    --redis-db=$REDIS_DB \
    --jar-folder=$JAR_FOLDER"
