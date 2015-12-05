#!/bin/bash

# figure out project directory
sbin="`dirname "$0"`"
ROOT_DIR="`cd "$sbin/../"; pwd`"

# functions (mainly for processing command-line arguments)
def_usage() {
    cat <<EOM

Usage: $0 [options]
-d | --daemon=*     launches service as daemon process, e.g. --daemon=true/false
--usage | --help    displayes usage of the script
-t | --test         launches service in test mode

EOM
    exit 0
}

def_daemon() {
    OPTION_USE_DAEMON="${i#*=}"
    if [ "$OPTION_USE_DAEMON" == "-d" ]; then
        OPTION_USE_DAEMON="true"
    elif [ "$OPTION_USE_DAEMON" == "true" ]; then
        OPTION_USE_DAEMON="true"
    elif [ "$OPTION_USE_DAEMON" == "false" ]; then
        OPTION_USE_DAEMON=""
    else
        echo "[ERROR] Unrecognized value $OPTION_USE_DAEMON for '--daemon' option"
        echo "Run '--usage' to display possible options"
        exit 1
    fi
}

def_test_mode() {
    OPTION_TEST_MODE="${i#*=}"
    if [ "$OPTION_TEST_MODE" == "-t" ]; then
        OPTION_TEST_MODE="true"
    elif [ "$OPTION_TEST_MODE" == "--test" ]; then
        OPTION_TEST_MODE="true"
    else
        OPTION_TEST_MODE=""
    fi
}

# command-line options for start-up:
# -d | --daemon => runs service as a daemon process
for i in "$@"; do
    case $i in
        # daemon process on/off
        -d|--daemon=*) def_daemon
        shift ;;
        # display usage
        --usage|--help) def_usage
        shift ;;
        # test mode
        -t|--test) def_test_mode
        shift ;;
        *) ;;
    esac
done

# load default variables (Octohaven and Redis settings)
. "$ROOT_DIR/sbin/config.sh"

# check dependencies (python is always checked)
. "$ROOT_DIR/sbin/check-python.sh"

# call to prepare variable for service check, also check whether service is running or not
. "$ROOT_DIR/sbin/check-service.sh"

# Check whether service is already running, and if it is tell to stop and exit
if [ -n "$IS_SERVICE_RUNNING" ]; then
    echo "[ERROR] Service is already running under process $PROCESS_ID. Stop it first"
    exit 1
fi

# check Spark dependencies
. "$ROOT_DIR/sbin/check-spark.sh"

# check if we are using Docker
if [ -n "$USE_DOCKER" ]; then
    # check that Docker is set properly
    . "$ROOT_DIR/sbin/check-docker.sh"
    # launch Docker container and ensure that REDIS_HOST is set correctly
    . "$ROOT_DIR/sbin/docker-launch.sh"
fi

# select test mode if available
if [ -n "$OPTION_TEST_MODE" ]; then
    echo "[WARN] Launching service in test mode"
    . "$ROOT_DIR/bin/test-config.sh"
fi

# command to start service
RUN_SERVICE_COMMAND="$WHICH_PYTHON $ROOT_DIR/run_service.py \
    --host=$OCTOHAVEN_HOST \
    --port=$OCTOHAVEN_PORT \
    --spark-ui-address=$OCTOHAVEN_SPARK_UI_ADDRESS \
    --spark-master-address=$OCTOHAVEN_SPARK_MASTER_ADDRESS \
    --redis-host=$REDIS_HOST \
    --redis-port=$REDIS_PORT \
    --redis-db=$REDIS_DB \
    --jar-folder=$JAR_FOLDER"

if [ -n "$OPTION_USE_DAEMON" ]; then
    echo "[INFO] Launching service as daemon process..."
    eval "nohup $RUN_SERVICE_COMMAND 0<&- &>/dev/null &"
else
    echo "[INFO] Launching service as normal process..."
    eval "$RUN_SERVICE_COMMAND"
fi
