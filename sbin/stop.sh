#!/bin/bash

bin="`dirname "$0"`"
ROOT_DIR="`cd "$bin/../"; pwd`"

# Import functions
. "$ROOT_DIR/sbin/functions.sh"

# We potentially can have multiple PIDs for application, e.g. when launching with make
# So we have to shutdown all of them gracefully
function shutdown() {
  SIG="INT"
  # Resolve termination signal
  if [[ -n "$1" ]]; then
    SIG="$1"
  fi

  while [[ -n $(get_service_pids) ]]; do
    for pid in $(get_service_pids); do
      echo "Asked application process $pid to exit"
      kill -s $SIG $pid
      sleep 2
    done
  done
}

# Request application exit
shutdown "TERM"

# Stop docker container, report any errors if encounter
# Import current settings from configuration
. "$ROOT_DIR/conf/octohaven-env.sh"

# Resolve settings
if [[ "$(is_yes $USE_DOCKER)" == "ERROR" ]]; then
  echo "USE_DOCKER option has incorrect value $USE_DOCKER"
  exit 1
else
  USE_DOCKER=$(is_yes $USE_DOCKER)
fi

# If docker is used check docker, launch VM, pull image and start container
if [[ -n "$USE_DOCKER" ]]; then
  . "$ROOT_DIR/sbin/docker-env.sh"

  if [[ -n "$IS_DOCKER_CONTAINER_RUNNING" ]]; then
    echo "Container $OCTOHAVEN_CONTAINER_NAME is running. Attempt to stop it"
    eval "$DOCKER_AGENT stop $OCTOHAVEN_CONTAINER_NAME" || \
      (echo "[ERROR] Failed to stop. You can stop container $OCTOHAVEN_CONTAINER_NAME manually" && exit 1)
  fi

  if [[ -n "$IS_DOCKER_CONTAINER_EXISTS" ]]; then
    echo "Container $OCTOHAVEN_CONTAINER_NAME is stopped"
  else
    echo "Container $OCTOHAVEN_CONTAINER_NAME does not exist"
  fi
fi
