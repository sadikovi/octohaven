#!/bin/bash

bin="`dirname "$0"`"
ROOT_DIR="`cd "$bin/../"; pwd`"
echo "[INFO] Removing *.pyc files in $ROOT_DIR"
# delete .pyc files from project folder
for f in $(find "$ROOT_DIR" -name "*.pyc" -type file); do
    echo "- Removing $f"
    rm "$f"
done
echo "[INFO] Done"
