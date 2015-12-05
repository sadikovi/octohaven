#!/bin/bash

# figure out project directory
bin="`dirname "$0"`"
ROOT_DIR="`cd "$bin/../"; pwd`"

# define testing steps
RUN_UNIT_TESTS=""
RUN_INTEGRATION_TESTS=""

def_help() {
    cat <<EOM

Usage: $0 [options]
-u | --unittest     runs unit tests
-i | --integration  runs integration tests
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
        -i|--integration) RUN_INTEGRATION_TESTS="YES"
        shift ;;
        -h|--help) def_help
        shift ;;
        *) ;;
    esac
done

echo "[WARN] Tests will use Redis instance specified in config.sh"
echo "[WARN] Redis test db will be set in test-config.sh"
# load default variables (Octohaven and Redis settings)
. "$ROOT_DIR/sbin/config.sh"
# load default redis configuration, can override config.sh properties
. "$ROOT_DIR/bin/test-config.sh"

# check dependencies (python is always checked)
. "$ROOT_DIR/sbin/check-python.sh"

# check if we are using Docker
if [ -n "$USE_DOCKER" ]; then
    # check that Docker is set properly
    . "$ROOT_DIR/sbin/check-docker.sh"
    # launch Docker container and ensure that REDIS_HOST is set correctly
    . "$ROOT_DIR/sbin/docker-launch.sh"
fi

echo "[INFO] Running tests..."

################################################################
# Unit tests module
################################################################
if [ -n "$RUN_UNIT_TESTS" ]; then
    eval "$WHICH_PYTHON $ROOT_DIR/run_tests.py test $REDIS_HOST $REDIS_PORT $REDIS_TEST_DB" || \
        UNIT_TESTS_FAILED="YES"
else
    echo "[WARN] Skipped unit tests"
fi

# assess results, stop if unit tests failed
if [ -n "$UNIT_TESTS_FAILED" ]; then
    exit 1
fi

################################################################
# Integration tests
################################################################
if [ -n "$RUN_INTEGRATION_TESTS" ]; then
    # launch service in test mode, always top service afterwards
    eval "$ROOT_DIR/sbin/start.sh -d --test" && sleep 5 && \
    (eval "$WHICH_PYTHON $ROOT_DIR/run_integration_tests.py test $OCTOHAVEN_HOST $OCTOHAVEN_PORT" || \
        INTEGRATION_TESTS_FAILED="YES") && \
    eval "$ROOT_DIR/sbin/stop.sh"
else
    echo "[WARN] Skipped integration tests"
fi

# assess results, stop if integration tests failed
if [ -n "$INTEGRATION_TESTS_FAILED" ]; then
    exit 1
fi
