#!/bin/bash

# $1 - flag to either start machine and container or stop them
# $2 - machine name
# $3 - container name
export machine_exists=$(which docker-machine)
export container_host="localhost"

function start_docker_machine() {
  if [[ -n "$machine_exists" ]]; then
    docker-machine start $1
    eval $(docker-machine env $1)
  fi
}

function stop_docker_machine() {
  if [[ -n "$machine_exists" ]]; then
    docker-machine stop $1
  fi
}

function docker_interface() {
  if [[ $1 == "start" ]]; then
    start_docker_machine $2
    exists=$(docker ps -a | grep -e "\\s\+$3$")
    if [[ -n "$exists" ]]; then
      docker start $3
    else
      docker run -h sandbox -p 3306:3306 --name $3 \
        -e MYSQL_ROOT_PASSWORD=12345 -e MYSQL_USER=user -e MYSQL_PASSWORD=12345 \
        -e MYSQL_DATABASE=octohaven -d mysql:5.7
    fi
  else
    eval $(docker-machine env $2)
    docker stop $3
    stop_docker_machine $2
  fi
}

function docker_get_host() {
  if [[ -n "$machine_exists" ]]; then
    start_docker_machine $1
    container_host=$(docker-machine ip $(docker-machine active))
  else
    container_host="localhost"
  fi
}
