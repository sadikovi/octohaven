#!/bin/bash

# [NOTE] this script should be loaded after configuration, since we are using container name

# find docker and check running container
export WHICH_DOCKER=$(which docker)
if [ -z "$WHICH_DOCKER" ]; then
    echo "[ERROR] Docker is not found."
    exit 1
fi

# also find docker-machine
export WHICH_DOCKER_MACHINE=$(which docker-machine)
if [ -z "$WHICH_DOCKER_MACHINE" ]; then
    echo "[INFO] Running on Linux environment. No need for docker-machine"
fi

# check that docker daemon is running and available
DOCKER_OK="$($WHICH_DOCKER version | grep Server)"
if [ -z "$DOCKER_OK" ]; then
    echo "[ERROR] Problems with Docker daemon. Try restarting service"
    exit 1
fi

# extract docker server version, using awk and grep, since command
# "docker version --format '{{.Server.Version}}'" fails for older versions < 1.6.0
export DOCKER_SERVER_VERSION=$($WHICH_DOCKER version | awk '{ind=($0~/Server/)?ind+1:ind}
    {if (ind && $0~/Version/) print $2}' | grep -e '[[:digit:]]\.[[:digit:]]\.[[:digit:]]')

# check if container exists and running
export DOCKER_CONTAINER_EXISTS=$($WHICH_DOCKER ps -a | grep -e "\\s\+$DOCKER_CONTAINER$")
export DOCKER_CONTAINER_RUNNING=$($WHICH_DOCKER ps | grep -e "\\s\+$DOCKER_CONTAINER$")
