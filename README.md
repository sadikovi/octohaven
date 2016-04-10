# octohaven
Super simple Apache Spark job server.

Latest release: [v1.1.0](https://github.com/sadikovi/octohaven/releases/latest)

- [Overview](#overview)
- [Dependencies](#dependencies)
- [Install and run](#install-and-run)
- [Quick test](#quick-test)
- [Application logs](#application-logs)
- [Spark job logs](#spark-job-logs)
- [Configuration](#configuration)
- [Build and test](#build-and-test)
- [Create release](#create-release)
- [Contribute](#contribute)

## Overview
Simple Spark job scheduler, allows to run created, delayed or periodic jobs with selected `jar` file
and Spark configuration/job attributes, keeps history of all jobs launched.

Features:
- templates to quickly create jobs
- delayed jobs (run after specific time period)
- periodic jobs (run jobs periodically using timetables and Cron expressions)
- view `stdout`/`stderr` of jobs using UI and etc.
- does not mess up with Spark cluster installation and/or scripts (more like nice feature, which
  you can easily turn on/off any time)
- Tested only with Spark standalone cluster, not sure if it will work with Yarn or Mesos

## Dependencies
- OS X or Linux, **octohaven** does not support Windows, yet
- Python 2.7, technically it can run on any `>2.3` distributions, but `2.7` is forced currently
- **octohaven** has to run side-by-side with Apache Spark (on the same machine/vm). Usually I use it
on the same VM where Spark master is.

See [Configuration](#configuration) on how to configure **octohaven**.

## Install and run
Download one of the distributions `octohaven-x.y.z.tar.gz` or `octohaven-x.y.z.zip`, unpack archive,
and edit a few configuration parameters in `conf/octohaven-env.sh` (see [Configuration]($configuration)).
```shell
$ tar xzvf octohaven-1.0.0.tar.gz
$ vi conf/octohaven-env.sh
```
Launch application:
```shell
$ sbin/start.sh
```
`start.sh` provides options:
- `--daemon`, `-d`    launch service as daemon process, e.g. --daemon=true/false
- `--help`            display usage of the script
- `--test`, `-t`      launch service in test mode, e.g. --test
- `--python`          provide different location of PYTHON_EXE, default is /usr/bin/python

Note that `start.sh` will also launch and manage docker container for you, if you have chosen to
use docker in configuration (recommended).

To stop application, this will also try to stop docker container, if docker is used with **octohaven**.
```shell
$ sbin/stop.sh
```

## Quick test
Once **octohaven** is running, it will show you current availability of the Spark cluster and list
history of jobs that you have run (should be empty). You can run quick test to see how it works.
Create job with settings (note, that you might need to change jar folder directly, or you can copy
jar into your directory):
- entrypoint: `org.test.SparkSum`
- jar: `test/resources/filelist/prod/start-sbt-app_2.10-0.0.1.jar`
- job options: any number up to max integer

Job will report sum of numbers between 0 and number specified. You could also try viewing stdout
and stderr during progress of the job.

## Application logs
**octohaven** stores application logs in current project directory, and uses `conf/log.conf`
configuration for logging. You can specify different location or settings in that file.

## Spark job logs
**octohaven** also stores logs (stdout and stderr) produced during run of the job. They are stored in
working directory, which defaults to `work/` in project directory. You can configure it in
`conf/octohaven-env.sh`.

## Configuration
All configuration is in `conf/octohaven-env.sh`. Available options are listed below
(also well-documented in the configuration file):
- `OCTOHAVEN_HOST`, `OCTOHAVEN_PORT` host and port for the service
- `OCTOHAVEN_SPARK_MASTER_ADDRESS`, `OCTOHAVEN_SPARK_UI_ADDRESS`
- `JAR_FOLDER` starting folder/root, it will traverse directory to look for jar files
- `WORKING_DIR` working directory, where job logs are stored, defaults to `work/`
- `NUM_SLOTS` number of slots, defines number of jobs allowed to be launched or running at the same
  time. This includes all jobs launched by application as well as Spark cluster, defaults to `1`
- `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` MySQL settings to
  access provided database. Note that if you choose to use docker, you do not need to change
  parameters, it will work out of the box (unless you want to change passwords, etc.)
- `USE_DOCKER` whether or not use docker container to store data, if yes, it will automatically pull
  image and launch container with MySQL settings above.
- `OCTOHAVEN_CONTAINER_NAME` name of the docker container to launch

## Build and test
To build the project you need to setup virtual environment first, it is recommended to use `venv`
folder, since `bin` scripts have nice wrappers for this.
```shell
$ git clone https://github.com/sadikovi/octohaven
$ cd octohaven
$ virtualenv venv
```

Docker is used for development and running tests. Make sure that you invoke this to setup
docker-machine (if available), and docker container.
```shell
$ make docker-start
```
This will start `default` VM, if docker-machine exists, and launch test container. This is pretty
much the entry point to work on **octohaven**. You can use `make docker-stop` to shutdown container,
and/or docker-machine.

Clean current directory, e.g. remove dependencies, `*.pyc`, `*.log`, distribution files, etc.
```shell
$ make clean
```

Build dependencies and source files use (mostly when working on front-end):
```shell
$ make build
```
Building coffee and SCSS files requires `coffee`, `sass`, and `uglifyjs`. Script will warn you, if
you do not have either of these packages, and suggest how to install them.
```shell
$ gem install sass
$ npm install coffee-script
$ npm install uglifyjs
```

Actually start service. Assumes that you already have run `make docker-start`.
```
$ make start
```
This will start service with default parameters in non-daemon mode, should work in any environment.
Just make sure to look into `makefile` and tweak it for yourself, currently there is not much of
automation, so you might need to change manually MySQL host/container host in connection string. To
stop service use `Ctrl-C` in terminal.

Run unit tests. Assumes that you already have run `make docker-start`.
```shell
$ make test
```

Use `bin/python` and `bin/pip` to use `python` and `pip` respectively to use virtual environment
installation.

## Create release
To create release follow these steps. Currently there are some manual interventions, but I will
automate it as much as I can later.
```shell
# 1. Launch docker container
$ make docker-start

# 2. Change version in 'version.py', 'package.json', 'bower.json'

# 3. Change logging and debugging mode in 'log.conf', 'internal.py', if necessary

# 4. Change README latest release link

# 5. Make distribution:
# Clean project directory, download dependencies, build source files, run unit-tests,
# create zip and tar archives
$ make dist

# 6. Commit changes into GitHub
$ git add --all
$ git commit -m "release version x.y.z"
$ git push

# 7. Create release/tag on GitHub
# Also upload archives from 'dist' folder as binaries for new release/tag

# 8. Pull changes, and turn dev mode on:
# update next version in 'version.py', 'package.json', 'bower.json'
# update logging and debugging in 'log.conf', 'internal.py' if applicable
$ git pull
$ git commit -m "set up next version dev mode"
$ git push
```

## Contribute
All suggestions, features, issues and PRs are very welcome:)
