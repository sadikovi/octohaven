# octohaven
Super simple Apache Spark job server.

- [Overview](#overview)
- [Install](#install)
- [Run](#run)
    - [Quick test](#quick-test)
    - [Spark job logs](#spark-job-logs)
- [Configuration](#configuration)
- [Build and test](#build-and-test)

## Overview
Allows you to select `jar` file and specify Spark conf parameters. You can schedule jobs to run
after some time passed, pass job parameters along with Spark configuration and etc, though you
cannot monitor job and see progress yet.

## Install
Super simple install and no dependencies, except Python 2.7.x, and Redis.
Uses Docker to install Redis, but can use your own installation, see [Configuration](#configuration)

## Run
Download repository and run scripts from `sbin` directory.
To run service execute `start.sh` script, to stop service - `stop.sh`. Application will be
available on `localhost:33900` or whatever port you will have specified in `config.sh`.

```shell
# start service, this will load configuration from config.sh
$ sbin/start.sh
```

```shell
# stop service
$ sbin/stop.sh
```

Application will be available on `localhost:33900` or whatever port you specify in configuration
file.

### Quick test
There is a jar file in distribution, so you can try running sample Spark job out of the box.
Settings are:
- **entrypoint** org.test.SparkSum
- **jar** projectDir/test/resources/filelist/prod/start-sbt-app_2.10-0.0.1.jar
- **jobconf** any number up to max integer

Job will report sum of numbers between 0 and number specified.

### Spark job logs
Each job saves `stdout` and `stderr` results in global log folder `projectDir/apache/spark/logs`.
Folder is created for each job with `job.uid` as name, with structure as follows:
- folder (job uid)
    - `stdout` (process stdout)
    - `stderr` (process stderr)
    - `_metadata` (job information, e.g. uid, name, options and etc.)

Here is an example:
```shell
+-- apache/spark/logs/
    +-- job_02488ad5381f416ea271f20359756874/
        +-- _metadata
        +-- stderr
        +-- stdout
    +-- job_6efada24b5484e9bb835f6dd379168cd/
        +-- _metadata
        +-- stderr
        +-- stdout
```

## Configuration
Configuration lives in `sbin/config.sh`. Options are pretty self-explanatory, comments tell what
options mean. It is recommended to use Docker, as it makes life easier, but you also have an
option to specify host, port, db of the running instance.

## Build and test
There is no building project really, you just run tests to verify that Python modules work. For
front-end you will be asked to install `coffee`, `sass` to compile scripts.
```shell
# to build front-end scripts - CoffeeScript and SCSS
$ bin/compile.sh
```

To run tests execute command below. Be aware, that tests use db `15` of Redis instance, although it
will check whether your production db and test db have the same number, it is worth changing it, if
your db also uses db '15', you can do it by changing db in configuration or `bin/test.sh`.
```shell
# run Python tests
$ bin/test.sh
```

Sometimes it is annoying to see `*.pyc` files everywhere. Run cleanup script to remove them.
```shell
$ bin/cleanup.sh
```
