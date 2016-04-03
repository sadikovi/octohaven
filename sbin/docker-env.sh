#!/bin/bash

bin="`dirname "$0"`"
ROOT_DIR="`cd "$bin/../"; pwd`"

# Script to extract all Docker related variables and checks
# It relies on container name which comes from configuration, therefore has to loaded after it.
if [[ -z "$OCTOHAVEN_CONTAINER_NAME" ]]; then
  echo "[ERROR] Container name is not set, please set OCTOHAVEN_CONTAINER_NAME"
  exit 1
fi

export DOCKER_AGENT=$(which docker)
if [[ -z "$DOCKER_AGENT" ]]; then
  echo "[ERROR] Docker is not found. Cannot launch container"
  exit 1
fi

export DOCKER_VM=$(which docker-machine)
if [[ -n "$DOCKER_VM" ]]; then
  echo "[INFO] Running on non-Linux environment. Will check if docker daemon is running"
fi

export IS_DOCKER_OK="$($DOCKER_AGENT version | grep Server)"
if [[ -z "$IS_DOCKER_OK" ]]; then
  echo "[ERROR] Problems with Docker daemon. Try restarting docker, or vm"
  exit 1
fi

export IS_DOCKER_CONTAINER_EXISTS=$($DOCKER_AGENT ps -a | grep -e "\\s\+$OCTOHAVEN_CONTAINER_NAME$")
export IS_DOCKER_CONTAINER_RUNNING=$($DOCKER_AGENT ps | grep -e "\\s\+$OCTOHAVEN_CONTAINER_NAME$")
