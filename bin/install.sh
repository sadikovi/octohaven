#!/bin/bash

# Script to install all dependencies for project

bin="`dirname "$0"`"
ROOT_DIR="`cd "$bin/../"; pwd`"

# create temporary directory for artifacts
EXTERNAL_LIB_DIR="$ROOT_DIR/temp/external"
if [[ -d "$EXTERNAL_LIB_DIR" ]]; then
    echo "[INFO] Clean up $EXTERNAL_LIB_DIR"
    rm -r "$EXTERNAL_LIB_DIR"
fi
mkdir -p "$EXTERNAL_LIB_DIR"

################################################################
# Install MySQL connector
################################################################
if [[ -d "$ROOT_DIR/lib/mysql" ]]; then
    echo "[INFO] Removing previous MySQL connector installation"
    rm -r "$ROOT_DIR/lib/mysql"
fi

echo "[INFO] Installing MySQL connector"
# copy tar archive into temp, unzip it, and build it
MYSQL_CONNECTOR="mysql-connector-python-rf-2.1.3"
curl -sL https://pypi.python.org/packages/source/m/mysql-connector-python-rf/"$MYSQL_CONNECTOR.tar.gz" | \
    tar xz -C "$EXTERNAL_LIB_DIR"
# then copy content of build/ folder into lib
(cd "$EXTERNAL_LIB_DIR/$MYSQL_CONNECTOR" && python setup.py build --build-lib="$EXTERNAL_LIB_DIR") && \
    cp -R "$EXTERNAL_LIB_DIR/mysql" "$ROOT_DIR/lib/"
