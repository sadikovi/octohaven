#!/bin/bash

# figure out project directory
bin="`dirname "$0"`"
ROOT_DIR="`cd "$bin/../"; pwd`"

# define testing steps
RUN_UNIT_TESTS=""

def_help() {
    cat <<EOM

Usage: $0 [options]
-u | --unittest     runs unit tests
-h | --help         displayes usage of the script

EOM
    exit 0
}

# command-line options for start-up:
# -d | --daemon => runs service as a daemon process
for i in "$@"; do
    case $i in
        -u|--unittest) RUN_UNIT_TESTS="YES"
        shift ;;
        -h|--help) def_help
        shift ;;
        *) ;;
    esac
done

echo "[WARN] Tests will use docker to launch test MySQL instance specified in test-config.sh"

# load default configuration, some testing related options will be overwritten
. "$ROOT_DIR/sbin/config.sh"

# load test configuration
. "$ROOT_DIR/bin/test-config.sh"

# check dependencies (python is always checked)
. "$ROOT_DIR/sbin/check-python.sh"

# force using docker for tests
. "$ROOT_DIR/sbin/check-docker.sh"
. "$ROOT_DIR/sbin/docker-launch.sh"

# run setup command
eval "$WHICH_PYTHON $ROOT_DIR/setup.py \
    user=$MYSQL_USER \
    password=$MYSQL_PASSWORD \
    host=$MYSQL_HOST \
    port=$MYSQL_PORT \
    database=$MYSQL_DATABASE \
    drop_existing=YES" || exit 1

echo "[INFO] Running tests..."

################################################################
# Unit tests module
################################################################
if [ -n "$RUN_UNIT_TESTS" ]; then
    eval "$WHICH_PYTHON $ROOT_DIR/run_unittests.py \
        user=$MYSQL_USER \
        password=$MYSQL_PASSWORD \
        host=$MYSQL_HOST \
        port=$MYSQL_PORT \
        database=$MYSQL_DATABASE" || UNIT_TESTS_FAILED="YES"
else
    echo "[WARN] Skipped unit tests"
fi

echo "[INFO] Stop container..."
eval "$WHICH_DOCKER stop $DOCKER_CONTAINER"

# assess results, stop if unit tests failed
if [ -n "$UNIT_TESTS_FAILED" ]; then
    exit 1
fi

# if no fail tests display success message
echo "All good!"
