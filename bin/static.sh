#!/bin/bash

bin="`dirname "$0"`"
ROOT_DIR="`cd "$bin/../"; pwd`"


# check if user has sass and coffee, and uglifyjs
WHICH_SASS=$(which sass)
if [ -z "$WHICH_SASS" ]; then
    echo "[ERROR] Cannot compile .scss scripts. Run 'gem install sass' to install"
    exit 1
fi

WHICH_COFFEE=$(which coffee)
if [ -z "$WHICH_COFFEE" ]; then
    echo "[ERROR] Cannot compile .coffee scripts. Run 'npm install coffee-script' to install"
    exit 1
fi

WHICH_UGLIFYJS=$(which uglifyjs)
if [ -z "$WHICH_UGLIFYJS" ]; then
    echo "[ERROR] Cannot minify js files using uglifyjs. Run 'npm install uglifyjs' to install"
    exit 1
fi

# main entrypoint for all static artifacts
STATIC_DIR="$ROOT_DIR/static"

# compile scss -> css and minify css
echo "[INFO] .scss >>> .css"
$WHICH_SASS "$STATIC_DIR/scss/internal.scss" "$STATIC_DIR/octohaven.min.css" --style compressed --sourcemap=none

# compile coffee -> js
# we compile javascript into temp directory and then compress them in particular order and put it
# back into "static"
echo "[INFO] Create 'temp' folder if does not exist"
TEMP_DIR="$ROOT_DIR/temp/target/js"
mkdir -p "$TEMP_DIR"

echo "[INFO] .coffee >>> .js"
$WHICH_COFFEE --no-header --compile --output "$TEMP_DIR" "$STATIC_DIR/coffee"

echo "[INFO] Compress preload functions (timezone, ...) >> octohaven.preload.min.js"
$WHICH_UGLIFYJS $TEMP_DIR/preload/timezone.js -o "$STATIC_DIR/octohaven.preload.min.js" -c -m

# compress scripts in specific order, because of the dependencies
echo "[INFO] Compress utilities folder >> util.min.js"
$WHICH_UGLIFYJS \
    $TEMP_DIR/utilities/util.js \
    $TEMP_DIR/utilities/loader.js \
    $TEMP_DIR/utilities/mapper.js \
    $TEMP_DIR/utilities/fasteditor.js \
    $TEMP_DIR/utilities/api.js \
    -o "$STATIC_DIR/octohaven.util.min.js" -c -m

echo "[INFO] Compress 'create_job.coffee'"
$WHICH_UGLIFYJS $TEMP_DIR/createjob.js -o "$STATIC_DIR/octohaven.createjob.min.js" -c -m

echo "[INFO] Clean up target folder for JS"
rm -r "$TEMP_DIR"
