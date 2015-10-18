# octohaven
Super simple Apache Spark job server.

- [Overview](#overview)
- [Install](#install)
- [Run](#run)
- [Configuration](#configuration)
- [Build and test](#build-and-test)

# Overview
Allows you to select `jar` file and specify Spark conf parameters. Does not have ability to specify
job parameters, but there is an issue for that.

# Install
Super simple installation and no dependencies, except Python 2.7.x, and Redis
Uses Docker to install Redis, but can use your own installation, see [Configuration](#configuration)

Download repository and run scripts from `sbin` directory.
To run service execute `start.sh` script, to stop service - `stop.sh`
```shell
# start service, this will load configuration from config.sh
$ sbin/start.sh
```

```shell
# stop service
$ sbin/stop.sh
```

# Configuration
Configuration lives in `sbin/config.sh`. Options are pretty self-explanatory, comments tell what
options mean. It is recommended to use Docker, because it just makes life easier, but if you do not
want to use Docker for Redis, you will have to specify host, port, db of the running instance.

# Build and test
There is no building project really, you just run tests to verify that Python modules work. For
front-end you will be asked to install `coffee`, `sass` to compile scripts, if you have not already.
```shell
# to build front-end scripts - CoffeeScript and SCSS
$ bin/compile.sh
```

To run tests execute command below. Be aware, that tests use db `15` of Redis instance, so you use
it for something else, change value to some other in `bin/test.sh`
```shell
# run Python tests
$ bin/test.sh
```

Sometimes it is annoying to see `*.pyc` files everywhere. Run cleanup script to remove them.
```shell
$ bin/cleanup.sh
```
