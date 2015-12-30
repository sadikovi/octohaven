#!/bin/bash

bin="`dirname "$0"`"
ROOT_DIR="`cd "$bin/../"; pwd`"
# delete .pyc files from project folder
echo "[INFO] Removing *.pyc files in $ROOT_DIR"
for f in $(find "$ROOT_DIR" -name "*.pyc" -type f); do
    echo "- Removing $f"
    rm "$f"
done
# delete sass cache
echo "[INFO] Removing sass-cache files in $ROOT_DIR"
if [[ -d "$ROOT_DIR/.sass-cache" ]]; then
    echo "- Removing directory"
    rm -r "$ROOT_DIR/.sass-cache"
fi
# delete service logs
echo "[INFO] Removing 'octohaven-service.log' files"
for f in $(find "$ROOT_DIR" -name "octohaven-service.log*" -type f); do
    echo "- Removing $f"
    rm "$f"
done
# delete apache/spark/logs dir and all subfolders
echo "[INFO] Removing 'apache/spark/logs' directory for Spark job logs"
OCTOHAVEN_SPARK_LOGS_DIR="$ROOT_DIR/apache/spark/logs"
for f in $(find "$OCTOHAVEN_SPARK_LOGS_DIR" -name "job*" -type d); do
    echo "- Removing $f"
    rm -r "$f"
done
# ... and we are done
echo "[INFO] Done"
