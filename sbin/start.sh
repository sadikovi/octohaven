#!/bin/bash

bin="`dirname "$0"`"
ROOT_DIR="`cd "$bin/../"; pwd`"

# Import functions
. "$ROOT_DIR/sbin/functions.sh"

# Command-line options for start-up:
for i in "$@"; do
  case $i in
    # Daemon process (true/false)
    -d|--daemon=*)
      OPTION_USE_DAEMON=$(resolve_daemon_opt)
    shift ;;
    # Display help
    --help)
      show_start_help
      exit 1
    shift ;;
    # Use test mode
    -t|--test)
      OPTION_TEST_MODE=$(resolve_test_opt)
    shift ;;
    *) ;;
  esac
done

# Find Python
PYTHON27=$(which python)
if [[ -z "$PYTHON27" ]]; then
  echo "[ERROR] Python is not found. Cannot work without python"
  exit 1
else
  PYTHON_VERSION=$(python_version $PYTHON27)
  if [[ ! "$PYTHON_VERSION" == "2.7" ]]; then
    echo "[ERROR] Python 2.7 required, found Python $PYTHON_VERSION"
    exit 1
  fi
fi

# Find "spark-submit"
SPARK_SUBMIT=$(which spark-submit)
if [[ -z "$SPARK_SUBMIT" ]]; then
  echo "[WARN] Cannot find 'spark-submit'. Fallback to SPARK_HOME"
  if [[ -n "$SPARK_HOME" ]]; then
    SPARK_SUBMIT="$SPARK_HOME/bin/spark-submit"
  fi
fi

# Find if service is already running
SERVICE_PID=$(get_service_pids)
if [[ -n "$SERVICE_PID" ]]; then
  echo "[ERROR] Service is already running, Shutdown current service process to start"
  exit 1
fi

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
  if [[ -z "$OCTOHAVEN_CONTAINER_NAME" ]]; then
    echo "[ERROR] Container name is not set, please set OCTOHAVEN_CONTAINER_NAME"
    exit 1
  fi

  DOCKER_AGENT=$(which docker)
  if [[ -z "$DOCKER_AGENT" ]]; then
    echo "[ERROR] Docker is not found. Cannot launch container"
    exit 1
  fi

  DOCKER_VM=$(which docker-machine)
  if [[ -n "$DOCKER_VM" ]]; then
    echo "[INFO] Running on non-Linux environment. Will check if docker daemon is running"
  fi

  IS_DOCKER_OK="$($DOCKER_AGENT version | grep Server)"
  if [[ -z "$IS_DOCKER_OK" ]]; then
    echo "[ERROR] Problems with Docker daemon. Try restarting docker, or vm"
    exit 1
  fi

  IS_DOCKER_CONTAINER_EXISTS=$($DOCKER_AGENT ps -a | grep -e "\\s\+$OCTOHAVEN_CONTAINER_NAME$")
  IS_DOCKER_CONTAINER_RUNNING=$($DOCKER_AGENT ps | grep -e "\\s\+$OCTOHAVEN_CONTAINER_NAME$")

  # Check that container exists and running and apply appropriate actions
  if [[ -z "$IS_DOCKER_CONTAINER_RUNNING" ]]; then
    if [[ -z "$IS_DOCKER_CONTAINER_EXISTS" ]]; then
      echo "[INFO] Launching new container $OCTOHAVEN_CONTAINER_NAME"
      LAUNCH_CMD="$DOCKER_AGENT run \
        -h $MYSQL_HOST \
        -p $MYSQL_PORT:3306 \
        --name $OCTOHAVEN_CONTAINER_NAME \
        -e MYSQL_ROOT_PASSWORD=$MYSQL_PASSWORD \
        -e MYSQL_USER=$MYSQL_USER \
        -e MYSQL_PASSWORD=$MYSQL_PASSWORD \
        -e MYSQL_DATABASE=$MYSQL_DATABASE \
        -d mysql:5.7"
      eval "$LAUNCH_CMD" || (echo "[ERROR] Failed to run new container. Try again later" && exit 1)
      echo "[INFO] Docker (<1.5.0) sometimes takes time to make container ready to connect."
      echo "  So MySQL might fail with ConnectionError. In this case try upgrading Docker to"
      echo "  latest version, or just relaunch service script (sbin/start.sh)"
    else
      echo "[INFO] Starting container $OCTOHAVEN_CONTAINER_NAME"
      eval "$DOCKER_AGENT start $OCTOHAVEN_CONTAINER_NAME" || \
        (echo "[ERROR] Failed to start container. Try again later." && exit 1)
    fi
    # Sleep for some time until container is ready
    sleep 3
  else
    echo "[INFO] Container $OCTOHAVEN_CONTAINER_NAME is already running"
  fi

  # If we use Docker we have to reevaluate host, as it will be VM IP in case of boot2docker
  # or localhost on Linux
  if [ -n "$DOCKER_VM" ]; then
    ACTIVE_VM=$($DOCKER_VM active)
    MYSQL_HOST=$($DOCKER_VM ip $ACTIVE_VM)
  else
    MYSQL_HOST="localhost"
  fi
  echo "[INFO] Updated host to connect $MYSQL_HOST"
fi

# Start service
SERVICE_COMMAND="$PYTHON27 $ROOT_DIR/setup.py start_octohaven \
  --host=$OCTOHAVEN_HOST \
  --port=$OCTOHAVEN_PORT \
  --spark-master=$OCTOHAVEN_SPARK_MASTER_ADDRESS \
  --spark-ui=$OCTOHAVEN_SPARK_UI_ADDRESS \
  --spark-submit=$SPARK_SUBMIT \
  --jar-folder=$JAR_FOLDER \
  --working-dir=$WORKING_DIR \
  --connection='jdbc:mysql://$MYSQL_HOST:$MYSQL_PORT/$MYSQL_DATABASE?user=$MYSQL_USER&password=$MYSQL_PASSWORD'"

if [[ -n "$OPTION_USE_DAEMON" ]]; then
  echo "[INFO] Launching service as daemon process"
  eval "nohup $SERVICE_COMMAND 0<&- &>/dev/null &"
else
  eval "$SERVICE_COMMAND"
fi
