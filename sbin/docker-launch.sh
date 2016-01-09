#!/bin/bash

# Script ensures that container is running by checking whether it exists and active, otherwise
# launches docker container with options provided from other scripts.
# [NOTE] Should be loaded after `check-docker.sh` and `config.sh`

# figure out project directory
bin="`dirname "$0"`"
ROOT_DIR="`cd "$bin/../"; pwd`"

# specifying image and version, hidden from configuration settings
MYSQL_IMAGE="mysql"
MYSQL_VERSION="5.7"

if [ -n "$DOCKER_CONTAINER_EXISTS" ]; then
    # verify that settings have not changed since, if they have, drop container
    INSPECT=$($WHICH_DOCKER inspect $DOCKER_CONTAINER)
    CHECKSUM=$(echo $INSPECT | \
        grep "\"Hostname\": \"$MYSQL_HOST\"" | \
        grep "\"HostPort\": \"$MYSQL_PORT\"" | \
        grep "\"MYSQL_USER=$MYSQL_USER\"" | \
        grep "\"MYSQL_PASSWORD=$MYSQL_PASSWORD\"" | \
        grep "\"MYSQL_DATABASE=$MYSQL_DATABASE\"")

    if [ -z "$CHECKSUM" ]; then
        echo "[WARN] Existing container does not match updated settings"
        echo "[INFO] Stopping and removing container $DOCKER_CONTAINER"
        eval "$WHICH_DOCKER stop $DOCKER_CONTAINER"
        DOCKER_CONTAINER_RUNNING=""
        eval "$WHICH_DOCKER rm $DOCKER_CONTAINER"
        DOCKER_CONTAINER_EXISTS=""
    fi
fi

# check if container exists and running
if [ -z "$DOCKER_CONTAINER_RUNNING" ]; then
    if [ -z "$DOCKER_CONTAINER_EXISTS" ]; then
        # run new container, as no container can be found
        # [issue #24] fail if anything goes wrong
        echo "[INFO] Running new container..."
        # we specify root password as user password
        eval "$WHICH_DOCKER run --name $DOCKER_CONTAINER -h $MYSQL_HOST -p $MYSQL_PORT:3306 \
            -e MYSQL_ROOT_PASSWORD=$MYSQL_PASSWORD -e MYSQL_USER=$MYSQL_USER \
            -e MYSQL_PASSWORD=$MYSQL_PASSWORD -e MYSQL_DATABASE=$MYSQL_DATABASE \
            -d $MYSQL_IMAGE:$MYSQL_VERSION" || exit 1
        # [issue #11] if Docker version is below 1.5.0, we have to launch container and then
        # invoke script "sbin/start.sh" again, otherwise it might fail with connection exception
        # "Error while reading from socket: (104, 'Connection reset by peer')"
        if [ -z "$DOCKER_SERVER_VERSION" ]; then
            echo "[WARN] Could not resolve Docker version"
        else
            # convert Docker version to integer by dropping "."
            DOCKER_SERVER_VERSION_NUM=$(echo $DOCKER_SERVER_VERSION | sed 's/\.//g')
            # show warning for Docker versions below 1.5.0
            if [ "$DOCKER_SERVER_VERSION_NUM" -lt "150" ]; then
                echo "[WARN] Docker version is less than 1.5.0 and not supported by application."
                echo "You can still run application, but MySQL might fail with connection error"
                echo "It is recommended to upgrade Docker to latest version."
                echo "To proceed or in case of error just try relaunching service"
                exit 0
            fi
        fi
    else
        # start stopped container, fail if anything goes wrong
        echo "[INFO] Starting up container..."
        eval "$WHICH_DOCKER start $DOCKER_CONTAINER" || exit 1
    fi
else
    echo "[INFO] Container is already running..."
fi

# if we use Docker we have to reevaluate host, as it will be VM IP in case of boot2docker
# or localhost on Linux
if [ -n "$WHICH_DOCKER_MACHINE" ]; then
    ACTIVE_VM=$($WHICH_DOCKER_MACHINE active)
    UPDATED_HOST=$($WHICH_DOCKER_MACHINE ip $ACTIVE_VM)
else
    UPDATED_HOST="localhost"
fi

# override REDIS_HOST when we use docker
export MYSQL_HOST="$UPDATED_HOST"
