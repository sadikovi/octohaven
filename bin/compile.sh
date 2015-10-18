#!/bin/bash

bin="`dirname "$0"`"
ROOT_DIR="`cd "$bin/../"; pwd`"

# check if user has sass and coffee
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

# compile scss -> css and minify css
echo "[INFO] .scss >>> .css"
sass "$ROOT_DIR/service/scss/internal.scss" "$ROOT_DIR/service/css/internal.min.css" \
    --style compressed --sourcemap=none
# compile coffee -> js
echo "[INFO] .coffee >>> .js"
coffee --compile --output "$ROOT_DIR/service/js" "$ROOT_DIR/service/coffee"
# and minify js
# uglifyjs static/js/loader.js -o foo.min.js -c -m
