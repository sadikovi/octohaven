#!/bin/sh

# figure out project directory
sbin="`dirname "$0"`"
ROOT_DIR="`cd "$sbin/../"; pwd`"

# load default variables (Octohaven and Redis settings)
. "$ROOT_DIR/sbin/config.sh"
# check dependencies
. "$ROOT_DIR/sbin/check.sh"

# stop docker container
DOCKER_REDIS_RUNNING=$(docker ps | grep -e "$REDIS_CONTAINER$")

if [ -n "$DOCKER_REDIS_RUNNING" ]; then
    echo "[INFO] Stopping Redis container..."
    eval "$WHICH_DOCKER stop $REDIS_CONTAINER"
else
    echo "[INFO] Redis container is already stopped"
fi

# stop serving
echo "[INFO] Stopping service..."
# start serving
PROCESS_ID=$(ps aux | grep "$WHICH_PYTHON $ROOT_DIR/run_service.py $OCTOHAVEN_PORT" | grep -v grep | awk '{print $2}')
if [ -z "$PROCESS_ID" ]; then
    echo "[INFO] Nothing to stop"
else
    kill $PROCESS_ID
    echo "[INFO] Stopped"
fi
