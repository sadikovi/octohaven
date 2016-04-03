#!/bin/bash

# Parse Yes/No variable
# args: $1 - variable to check
function is_yes() {
  if [[ "$1" == "YES" ]]; then
    echo "YES"
  elif [[ "$1" == "NO" ]]; then
    echo ""
  elif [[ -z "$1" ]]; then
    echo ""
  else
    echo "ERROR"
  fi
}

# Obtain Python version
# args: $1 - Python destination, e.g. /usr/bin/python
function python_version() {
  echo $($1 -c 'import sys; print ".".join([str(x) for x in sys.version_info[0:2]])')
}

# Return current active service PID/s
function get_service_pids() {
  echo $(ps aux | grep "setup.py start_octohaven" | grep -v grep | awk '{print $2}')
}

# Function to show help for the start script
function show_start_help() {
cat <<EOM
Usage: $0 [options]
  --daemon, -d      launch service as daemon process, e.g. --daemon=true/false
  --help            display usage of the script
  --test, -t        launch service in test mode, e.g. --test
  --python          provide different location of PYTHON_EXE, default is /usr/bin/python
EOM
}

# Function to resolve daemon option
function resolve_daemon_opt() {
  OPTION_USE_DAEMON="${i#*=}"
  if [[ "$OPTION_USE_DAEMON" == "-d" ]]; then
    echo "true"
  elif [[ "$OPTION_USE_DAEMON" == "true" ]]; then
    echo "true"
  elif [[ "$OPTION_USE_DAEMON" == "false" ]]; then
    echo ""
  else
    echo "ERROR"
  fi
}

# Function to resolve test option
function resolve_test_opt() {
  OPTION_TEST_MODE="${i#*=}"
  if [[ "$OPTION_TEST_MODE" == "-t" ]]; then
    echo "true"
  elif [[ "$OPTION_TEST_MODE" == "--test" ]]; then
    echo "true"
  else
    echo ""
  fi
}

# Function to resolve python executable
function resolve_python() {
  OPTION_PYTHON="${i#*=}"
  if [ -f $OPTION_PYTHON ]; then
    echo "$OPTION_PYTHON"
  else
    echo "ERROR"
  fi
}
