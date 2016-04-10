#!/bin/bash

bin="`dirname "$0"`"
ROOT_DIR="`cd "$bin/../"; pwd`"

# check if user has sass and coffee, and uglifyjs
if [ -z "$(which sass)" ]; then
  echo "[ERROR] Cannot compile .scss scripts. Run 'gem install sass' to install"
  exit 1
fi

if [ -z "$(which coffee)" ]; then
  echo "[ERROR] Cannot compile .coffee scripts. Run 'npm install coffee-script' to install"
  exit 1
fi

if [ -z "$(which uglifyjs)" ]; then
  echo "[ERROR] Cannot minify js files using uglifyjs. Run 'npm install uglifyjs' to install"
  exit 1
fi

# Main entrypoint for all static artifacts
STATIC_DIR="$ROOT_DIR/static"

# Compile scss -> css and minify css
echo "Compile SCSS into CSS"
sass "$STATIC_DIR/scss/internal.scss" "$STATIC_DIR/octohaven.min.css" --style compressed --sourcemap=none

# Compile coffee -> js
# Compile scripts that are preloaded before page
echo "Compile preload scripts"
cat $STATIC_DIR/coffee/preload/*.coffee | \
  coffee --no-header --compile --stdio | uglifyjs - -o "$STATIC_DIR/octohaven.preload.min.js" -c -m

# Common coffee files for build
UTIL_CMD="$STATIC_DIR/coffee/utilities/namer.coffee \
  $STATIC_DIR/coffee/utilities/util.coffee \
  $STATIC_DIR/coffee/utilities/loader.coffee \
  $STATIC_DIR/coffee/utilities/api.coffee \
  $STATIC_DIR/coffee/base.coffee"

echo "Compile 'jobs' scripts"
cat $UTIL_CMD $STATIC_DIR/coffee/jobs.coffee | \
  coffee --bare --no-header --compile --stdio | uglifyjs - -o "$STATIC_DIR/octohaven.jobs.min.js" -c -m

echo "Compile 'create-job' scripts"
cat $UTIL_CMD $STATIC_DIR/coffee/create_job.coffee | \
  coffee --bare --no-header --compile --stdio | uglifyjs - -o "$STATIC_DIR/octohaven.createjob.min.js" -c -m

echo "Compile 'job' scripts"
cat $UTIL_CMD $STATIC_DIR/coffee/job.coffee | \
  coffee --bare --no-header --compile --stdio | uglifyjs - -o "$STATIC_DIR/octohaven.job.min.js" -c -m

echo "Compile 'job-log' scripts"
cat $UTIL_CMD $STATIC_DIR/coffee/job_log.coffee | \
  coffee --bare --no-header --compile --stdio | uglifyjs - -o "$STATIC_DIR/octohaven.joblog.min.js" -c -m

echo "Compile 'timetables' scripts"
cat $UTIL_CMD $STATIC_DIR/coffee/timetables.coffee | \
  coffee --bare --no-header --compile --stdio | uglifyjs - -o "$STATIC_DIR/octohaven.timetables.min.js" -c -m

echo "Compile 'create-timetable' scripts"
cat $UTIL_CMD $STATIC_DIR/coffee/create_timetable.coffee | \
  coffee --bare --no-header --compile --stdio | uglifyjs - -o "$STATIC_DIR/octohaven.createtimetable.min.js" -c -m

echo "Compile 'timetable' scripts"
cat $UTIL_CMD $STATIC_DIR/coffee/timetable.coffee | \
  coffee --bare --no-header --compile --stdio | uglifyjs - -o "$STATIC_DIR/octohaven.timetable.min.js" -c -m

echo "Compile 'api' scripts"
cat $UTIL_CMD $STATIC_DIR/coffee/api.coffee | \
  coffee --bare --no-header --compile --stdio | uglifyjs - -o "$STATIC_DIR/octohaven.api.min.js" -c -m
