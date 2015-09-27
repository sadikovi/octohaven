#!/bin/sh

# find python to run server
export WHICH_PYTHON=$(which python)
if [ -z "$WHICH_PYTHON" ]; then
    echo "[ERROR] Python is not found. Cannot work without python"
    exit 1
fi

# find docker and check running redis container
export WHICH_DOCKER=$(which docker)
if [ -z "$WHICH_DOCKER" ]; then
    echo "[ERROR] Docker is not found. Cannot start Redis server"
    exit 1
fi

# check that docker daemon is running and available
DOCKER_OK="$(docker version | grep Server:)"
if [ -z "$DOCKER_OK" ]; then
    echo "[ERROR] Problems with Docker daemon. Try restarting service"
    exit 1
fi
