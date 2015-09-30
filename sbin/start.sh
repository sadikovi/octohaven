#!/bin/sh

# figure out project directory
sbin="`dirname "$0"`"
ROOT_DIR="`cd "$sbin/../"; pwd`"

# load default variables (Octohaven and Redis settings)
. "$ROOT_DIR/sbin/config.sh"
# check dependencies
. "$ROOT_DIR/sbin/check.sh"

# check passed port to run, default is 33900
OCTOHAVEN_PORT="$1"
if [ -z "$OCTOHAVEN_PORT" ]; then
    OCTOHAVEN_PORT="$OCTOHAVEN_DEFAULT_PORT"
fi

# check if container exists and running
DOCKER_REDIS_EXISTS=$(docker ps -a | grep -e "$REDIS_CONTAINER$")
DOCKER_REDIS_RUNNING=$(docker ps | grep -e "$REDIS_CONTAINER$")

if [ -z "$DOCKER_REDIS_RUNNING" ]; then
    if [ -z "$DOCKER_REDIS_EXISTS" ]; then
        # run new container, as no container can be found
        echo "[INFO] Running new Redis container..."
        eval "$WHICH_DOCKER run -h $REDIS_HOST -p $REDIS_PORT:$REDIS_PORT --name $REDIS_CONTAINER -d redis:$REDIS_VERSION"
    else
        # start stopped container
        echo "[INFO] Starting up Redis container..."
        eval "$WHICH_DOCKER start $REDIS_CONTAINER"
    fi
else
    echo "[INFO] Redis is already running"
fi

# start serving
eval "$WHICH_PYTHON $ROOT_DIR/run_service.py \
    --port=$OCTOHAVEN_PORT \
    --spark-ui-address=$OCTOHAVEN_SPARK_UI_ADDRESS \
    --spark-master-address=$OCTOHAVEN_SPARK_MASTER_ADDRESS \
    --redis-host=$REDIS_HOST \
    --redis-port=$REDIS_PORT"

echo "root: $ROOT_DIR"
echo "octohaven port: $OCTOHAVEN_PORT"
echo "python: $WHICH_PYTHON"
echo "docker: $WHICH_DOCKER"
