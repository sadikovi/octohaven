#!/bin/bash

bin="`dirname "$0"`"
ROOT_DIR="`cd "$bin/../"; pwd`"
# compile scss -> css and minify css
sass "$ROOT_DIR/service/scss/internal.scss" "$ROOT_DIR/service/css/internal.min.css" \
    --style compressed --sourcemap=none
# compile coffee -> js
coffee --compile --output service/js service/coffee
# and minify js
# uglifyjs static/js/loader.js -o foo.min.js -c -m
