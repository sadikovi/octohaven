# octohaven
Super simple Apache Spark job server. _In development. You can download latest release 0.1.0_

- [Overview](#overview)
- [Install](#install)
- [Run](#run)
    - [Quick test](#quick-test)
    - [Application logs](#application-logs)
    - [Spark job logs](#spark-job-logs)
- [Configuration](#configuration)
- [Build and test](#build-and-test)
- [Contribute](#contribute)

## Overview
Simple Spark job scheduler, allows to run created, delayed or periodic jobs with selected `jar` and
Spark / job configuration options.

Features:
- delayed jobs (run after some time passed)
- periodic jobs (run jobs periodically using timetables and Cron expressions)
- view `stdout` / `stderr` of jobs using UI and etc.

Goodies:
- does not mess up with Spark cluster installation and/or scripts (more like nice feature, which
    you can easily turn on/off any time)

Others:
- Tested only with Spark standalone cluster, not sure if it will work with Yarn or Mesos

Screenshot of the UI:
![Screenshot](./resources/octohaven-screenshot.png)

## Install

## Run
### Quick test
### Application logs
### Spark job logs

## Configuration

## Build and test
To build the project you need to setup virtual environment and install dependencies.
```shell
$ git clone https://github.com/sadikovi/octohaven
$ cd octohaven
$ virtualenv venv
$ bin/pip install -r requirements.txt --target lib/
```

Use `bin/python` and `bin/pip` to use `python` and `pip` respectively, as it uses virtual
environment installation.

Once you set up the environment, compile static files (Coffeescript and SCSS).
```shell
$ bin/static.sh
```

After that you can launch service.
```shell
$ bin/python setup.py start_octohaven \
    --host=localhost \
    --port=33900 \
    --spark-master=spark://local.lan:7077 \
    --spark-ui=http://localhost:8080 \
    --jar-folder=/tmp \
    --connection=jdbc:mysql_connection_string
```

## Contribute
All suggestions, features, issues and PRs are very welcome:)
