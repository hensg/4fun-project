#!/bin/bash

DOCKER=`which docker`
DOCKER_COMPOSE=`which docker-compose`
APT=`which apt`

if [ "$APT" ]; then
  if [ -z "$DOCKER" ]; then
    echo Docker was not found, installing it...;
    sudo apt install docker-ce -y;
    sudo service docker start;
  else
    echo Docker exists;
  fi
  if [ -z "$DOCKER_COMPOSE" ]; then
    echo Docker compose was not found, installing it...;
    sudo apt install docker-compose -y;
  else
    echo Docker compose exists;
  fi
else
  echo We support only apt linux for now
fi
