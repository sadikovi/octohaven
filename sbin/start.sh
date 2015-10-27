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
            # [issue #11] if Docker version is below 1.5.0, we have to launch container and then
            # invoke script "sbin/start.sh" again, otherwise it might fail with "redis.exceptions.ConnectionError"
            # "Error while reading from socket: (104, 'Connection reset by peer')"
            if [ -n "$DOCKER_SERVER_VERSION" ]; then
                # convert Docker version to integer by dropping "."
                DOCKER_SERVER_VERSION_NUM=$(echo $DOCKER_SERVER_VERSION | sed 's/\.//g')
                # show warning for Docker versions below 1.5.0
                if [ "$DOCKER_SERVER_VERSION_NUM" -lt "150" ]; then
                    echo "[WARN] Docker version is less than 1.5.0 and not supported by application."
                    echo "You can still run application, but Redis might fail with redis.exceptions.ConnectionError."
                    echo "It is recommended to upgrade Docker to latest version."
                    echo "To proceed or in case of error just try relaunching 'sbin/start.sh'"
                    exit 0
                fi
            fi
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

# start serving
eval "$WHICH_PYTHON $ROOT_DIR/run_service.py \
    --host=$OCTOHAVEN_HOST \
    --port=$OCTOHAVEN_PORT \
    --spark-ui-address=$OCTOHAVEN_SPARK_UI_ADDRESS \
    --spark-ui-run-address=$OCTOHAVEN_SPARK_UI_RUN_ADDRESS \
    --spark-master-address=$OCTOHAVEN_SPARK_MASTER_ADDRESS \
    --redis-host=$REDIS_HOST \
    --redis-port=$REDIS_PORT \
    --redis-db=$REDIS_DB \
    --jar-folder=$JAR_FOLDER"
