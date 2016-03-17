#!/bin/bash

# $1 - flag to either start machine and container or stop them
# $2 - machine name
# $3 - container name
if [[ $1 == "start" ]]; then
    docker-machine start $2
    eval $(docker-machine env $2)
    docker start $3
else
    eval $(docker-machine env $2)
    docker stop $3
    docker-machine stop $2
fi
