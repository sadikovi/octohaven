#!/bin/sh

ROOT_DIR=$(pwd)
echo "[INFO] Removing *.pyc files in $ROOT_DIR"
# delete .pyc files from project folder
for f in $(find "$ROOT_DIR" -name *.pyc -type file); do
    rm "$f";
done
echo "[INFO] Done"
