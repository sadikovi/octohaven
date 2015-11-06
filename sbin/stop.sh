#!/bin/bash

# figure out project directory
sbin="`dirname "$0"`"
ROOT_DIR="`cd "$sbin/../"; pwd`"

# load default variables (Octohaven and Redis settings)
. "$ROOT_DIR/sbin/config.sh"

# check dependencies (python is always checked)
. "$ROOT_DIR/sbin/check-python.sh"

# call to prepare variable for service check
. "$ROOT_DIR/sbin/check-service.sh"

# stop serving
echo "[INFO] Stopping service..."
# check process id to find out whether we need to stop process
if [ -z "$PROCESS_ID" ]; then
    echo "[INFO] Nothing to stop"
else
    kill $PROCESS_ID
    echo "[INFO] Stopped"
fi

# check if we are using Docker and stop container if exists
# should also recognize whether container exists or not
echo "[INFO] Stopping Redis container..."
if [ -n "$USE_DOCKER" ]; then
    . "$ROOT_DIR/sbin/check-docker.sh"
    # stop docker container
    if [ -n "$DOCKER_REDIS_RUNNING" ]; then
        eval "$WHICH_DOCKER stop $REDIS_CONTAINER" || \
            (echo "[ERROR] Failed to stop. You can stop container manually" && exit 1)
    elif [ -n "$DOCKER_REDIS_EXISTS" ]; then
        echo "[INFO] Redis container is already stopped"
    else
        echo "[INFO] No container '$REDIS_CONTAINER' found."
    fi
fi
