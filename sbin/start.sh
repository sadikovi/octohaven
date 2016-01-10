#!/bin/bash

# figure out project directory
sbin="`dirname "$0"`"
ROOT_DIR="`cd "$sbin/../"; pwd`"

# functions (mainly for processing command-line arguments)
def_usage() {
    cat <<EOM

Usage: $0 [options]
-d | --daemon=*     launches service as daemon process, e.g. --daemon=true/false
--reset             reset application, remove all data
--usage | --help    displayes usage of the script

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

def_reset() {
    OPTION_RESET="${i#*=}"
    if [ "$OPTION_RESET" == "--reset" ]; then
        OPTION_RESET="true"
    else
        OPTION_RESET=""
    fi
}

# command-line options for start-up:
for i in "$@"; do
    case $i in
        # daemon process on/off
        -d|--daemon=*) def_daemon
        shift ;;
        # reset data
        --reset) def_reset
        shift ;;
        # display usage
        --usage|--help) def_usage
        shift ;;
        *) ;;
    esac
done

# load configuration variables
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
    # launch Docker container and ensure that host is set correctly
    . "$ROOT_DIR/sbin/docker-launch.sh"
fi

# setup sql instance
eval "$WHICH_PYTHON $ROOT_DIR/setup.py \
    user=$MYSQL_USER \
    password=$MYSQL_PASSWORD \
    host=$MYSQL_HOST \
    port=$MYSQL_PORT \
    database=$MYSQL_DATABASE \
    drop_existing=$OPTION_RESET" || exit 1

# command to start service
RUN_SERVICE_COMMAND=""

if [ -n "$OPTION_USE_DAEMON" ]; then
    echo "[INFO] Launching service as daemon process..."
    eval "nohup $RUN_SERVICE_COMMAND 0<&- &>/dev/null &"
else
    echo "[INFO] Launching service as normal process..."
    eval "$RUN_SERVICE_COMMAND"
fi
