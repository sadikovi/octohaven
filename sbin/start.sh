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
        *) ;;
    esac
done

# load default variables (Octohaven and Redis settings)
. "$ROOT_DIR/sbin/config.sh"

# check dependencies (python is always checked)
. "$ROOT_DIR/sbin/check-python.sh"

# call to prepare variable for service check
. "$ROOT_DIR/sbin/check-service.sh"

# check Spark dependencies
. "$ROOT_DIR/sbin/check-spark.sh"

# check if we are using Docker
if [ -n "$USE_DOCKER" ]; then
    . "$ROOT_DIR/sbin/check-docker.sh"

    # check if container exists and running
    if [ -z "$DOCKER_REDIS_RUNNING" ]; then
        if [ -z "$DOCKER_REDIS_EXISTS" ]; then
            # run new container, as no container can be found
            # [issue #24] fail if anything goes wrong
            echo "[INFO] Running new Redis container..."
            eval "$WHICH_DOCKER run -h $REDIS_HOST -p $REDIS_PORT:6379 --name $REDIS_CONTAINER -d redis:$REDIS_VERSION" || \
                (echo "[ERROR] Failed to run new container. Try again later" && exit 1)
            # [issue #11] if Docker version is below 1.5.0, we have to launch container and then
            # invoke script "sbin/start.sh" again, otherwise it might fail with "redis.exceptions.ConnectionError"
            # "Error while reading from socket: (104, 'Connection reset by peer')"
            if [ -z "$DOCKER_SERVER_VERSION" ]; then
                echo "[WARN] Could not resolve Docker version"
            else
                # convert Docker version to integer by dropping "."
                DOCKER_SERVER_VERSION_NUM=$(echo $DOCKER_SERVER_VERSION | sed 's/\.//g')
                # show warning for Docker versions below 1.5.0
                if [ "$DOCKER_SERVER_VERSION_NUM" -lt "150" ]; then
                    echo "[WARN] Docker version is less than 1.5.0 and not supported by application."
                    echo "You can still run application, but Redis might fail with redis.exceptions.ConnectionError."
                    echo "It is recommended to upgrade Docker to latest version."
                    echo "To proceed or in case of error just try relaunching 'sbin/start.sh'"
                    exit 0
                else
                    echo "[INFO] Keep running..."
                fi
            fi
        else
            # start stopped container, fail if anything goes wrong
            echo "[INFO] Starting up Redis container..."
            eval "$WHICH_DOCKER start $REDIS_CONTAINER" || \
                (echo "[ERROR] Failed to start container. Try again later." && exit 1)
        fi
    fi
    # if we use Docker we have to reevaluate Redis host, as it will be VM IP in case of boot2docker
    # or localhost on Linux
    if [ -n "$WHICH_DOCKER_MACHINE" ]; then
        ACTIVE_VM=$($WHICH_DOCKER_MACHINE active)
        REDIS_HOST=$($WHICH_DOCKER_MACHINE ip $ACTIVE_VM)
    else
        REDIS_HOST="localhost"
    fi
fi

# now we are ready to actually run service. Check whether service is already running, and if it is
# tell to stop and exit
if [ -n "$IS_SERVICE_RUNNING" ]; then
    echo "[ERROR] Service is already running under process $PROCESS_ID. Stop it first"
    exit 1
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
