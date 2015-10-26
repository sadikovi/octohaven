# octohaven
Super simple Apache Spark job server.

- [Overview](#overview)
- [Install](#install)
- [Run](#run)
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
