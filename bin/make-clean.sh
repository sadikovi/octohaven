#!/bin/bash

bin="`dirname "$0"`"
ROOT_DIR="`cd "$bin/../"; pwd`"

# delete .pyc files from project folder
for f in $(find "$ROOT_DIR" -name "*.pyc" -type f -not -path "$ROOT_DIR/venv/*"); do rm "$f"; done

# delete sass cache
rm -rf "$ROOT_DIR/.sass-cache"

# delete target directory
rm -rf "$ROOT_DIR/target"

# delete bower artifacts directory
rm -rf "$ROOT_DIR/bower_components"

# delete npm artifacts directory
rm -rf "$ROOT_DIR/node_modules"

# delete all javascript artefacts in static folder
rm -f $ROOT_DIR/static/*.js

# delete all css artefacts in static folder
rm -f $ROOT_DIR/static/*.css

# delete service logs
rm -f "$ROOT_DIR/octohaven-service.log*"

# delete .DS_Store files
for f in $(find "$ROOT_DIR" -name ".DS_Store" -type f); do rm "$f"; done

# delete distribution files (directory and generated MANIFEST)
rm -rf "$ROOT_DIR/dist"
rm -f "$ROOT_DIR/MANIFEST"
