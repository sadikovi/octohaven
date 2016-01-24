#!/bin/bash

bin="`dirname "$0"`"
ROOT_DIR="`cd "$bin/../"; pwd`"

# delete .pyc files from project folder
echo "[INFO] Removing *.pyc files in $ROOT_DIR"
for f in $(find "$ROOT_DIR" -name "*.pyc" -type f -not -path "$ROOT_DIR/venv/*"); do
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

# delete .DS_Store files
echo "[INFO] Removing '.DS_Store' files"
for f in $(find "$ROOT_DIR" -name ".DS_Store" -type f); do
    echo "- Removing $f"
    rm "$f"
done

# delete distribution files
echo "[INFO] Removing distribution files"
DIST_DIR="$ROOT_DIR/dist"
if [[ -d "$DIST_DIR" ]]; then
    echo "- Removing $DIST_DIR"
    rm -r "$DIST_DIR"
fi

if [[ -f "$ROOT_DIR/MANIFEST" ]]; then
    echo "-Removing MANIFEST"
    rm "$ROOT_DIR/MANIFEST"
fi

# ... and we are done
echo "[INFO] Done"
