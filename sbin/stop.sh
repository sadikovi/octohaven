#!/bin/bash

# figure out project directory
sbin="`dirname "$0"`"
ROOT_DIR="`cd "$sbin/../"; pwd`"

# load configuration variables
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
if [ -n "$USE_DOCKER" ]; then
    echo "[INFO] Stopping container..."
    . "$ROOT_DIR/sbin/check-docker.sh"
    # stop docker container
    if [ -n "$DOCKER_CONTAINER_RUNNING" ]; then
        eval "$WHICH_DOCKER stop $DOCKER_CONTAINER" || exit 1
    elif [ -n "$DOCKER_CONTAINER_EXISTS" ]; then
        echo "[INFO] Container is already stopped"
    else
        echo "[INFO] No container '$DOCKER_CONTAINER' found."
    fi
fi
