#!/bin/sh

bin="`dirname "$0"`"
ROOT_DIR="`cd "$bin/../"; pwd`"
echo "[INFO] Running tests..."
python "$ROOT_DIR/run_tests.py" test
