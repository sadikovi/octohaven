#!/bin/sh

ROOT_DIR=$(pwd)
echo "[INFO] Running tests..."
python "$ROOT_DIR/run_tests.py" test
