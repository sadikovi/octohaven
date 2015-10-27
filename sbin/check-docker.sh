#!/bin/bash

# find docker and check running redis container
export WHICH_DOCKER=$(which docker)
if [ -z "$WHICH_DOCKER" ]; then
    echo "[ERROR] Docker is not found. Cannot start Redis server"
    exit 1
fi

# also find docker-machine
export WHICH_DOCKER_MACHINE=$(which docker-machine)
if [ -z "$WHICH_DOCKER_MACHINE" ]; then
    echo "[INFO] Running on Linux environment. No need for docker-machine"
fi

# check that docker daemon is running and available
DOCKER_OK="$(docker version | grep Server)"
if [ -z "$DOCKER_OK" ]; then
    echo "[ERROR] Problems with Docker daemon. Try restarting service"
    exit 1
fi

# extract docker server version
export DOCKER_SERVER_VERSION=$(docker version --format '{{.Server.Version}}')
