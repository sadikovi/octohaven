#!/bin/bash

# Script ensures that Redis container is running by checking whether it exists and active,
# otherwise launches docker container with options provided from other scripts.
# [NOTE] Should be loaded after `check-docker.sh` and `config.sh`

# figure out project directory
bin="`dirname "$0"`"
ROOT_DIR="`cd "$bin/../"; pwd`"

# check if container exists and running
if [ -z "$DOCKER_REDIS_RUNNING" ]; then
    if [ -z "$DOCKER_REDIS_EXISTS" ]; then
        # run new container, as no container can be found
        # [issue #24] fail if anything goes wrong
        echo "[INFO] Running new Redis container..."
        eval "$WHICH_DOCKER run -h $REDIS_HOST -p $REDIS_PORT:6379 --name $REDIS_CONTAINER -d redis:$REDIS_VERSION" || \
            (echo "[ERROR] Failed to run new container. Try again later" && exit 1)
        # [issue #11] if Docker version is below 1.5.0, we have to launch container and then
        # invoke script "sbin/start.sh" again, otherwise it might fail with "redis.exceptions.ConnectionError"
        # "Error while reading from socket: (104, 'Connection reset by peer')"
        if [ -z "$DOCKER_SERVER_VERSION" ]; then
            echo "[WARN] Could not resolve Docker version"
        else
            # convert Docker version to integer by dropping "."
            DOCKER_SERVER_VERSION_NUM=$(echo $DOCKER_SERVER_VERSION | sed 's/\.//g')
            # show warning for Docker versions below 1.5.0
            if [ "$DOCKER_SERVER_VERSION_NUM" -lt "150" ]; then
                echo "[WARN] Docker version is less than 1.5.0 and not supported by application."
                echo "You can still run application, but Redis might fail with redis.exceptions.ConnectionError."
                echo "It is recommended to upgrade Docker to latest version."
                echo "To proceed or in case of error just try relaunching service"
                exit 0
            else
                echo "[INFO] Keep running..."
            fi
        fi
    else
        # start stopped container, fail if anything goes wrong
        echo "[INFO] Starting up Redis container..."
        eval "$WHICH_DOCKER start $REDIS_CONTAINER" || \
            (echo "[ERROR] Failed to start container. Try again later." && exit 1)
    fi
fi

# if we use Docker we have to reevaluate Redis host, as it will be VM IP in case of boot2docker
# or localhost on Linux
if [ -n "$WHICH_DOCKER_MACHINE" ]; then
    ACTIVE_VM=$($WHICH_DOCKER_MACHINE active)
    UPDATED_REDIS_HOST=$($WHICH_DOCKER_MACHINE ip $ACTIVE_VM)
else
    UPDATED_REDIS_HOST="localhost"
fi

# override REDIS_HOST when we use docker
export REDIS_HOST="$UPDATED_REDIS_HOST"
