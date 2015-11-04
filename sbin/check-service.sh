#!/bin/bash

# figure out project directory
sbin="`dirname "$0"`"
ROOT_DIR="`cd "$sbin/../"; pwd`"

# extracting process id depends on Python installation that we are using, so need to launch it
# after we have resolved Python home.

# check whether service is already running by checking process id
export PROCESS_ID=$(ps aux | grep "$WHICH_PYTHON $ROOT_DIR/run_service.py" | grep -v grep | awk '{print $2}')
# create variable to whether it is running or not
export IS_SERVICE_RUNNING=""
if [ -n "$PROCESS_ID" ]; then
    IS_SERVICE_RUNNING="YES"
fi
