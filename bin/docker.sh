#!/bin/bash

# $1 - machine name
# $2 - container name
docker-machine start $1
eval $(docker-machine env $1)
docker start $2
