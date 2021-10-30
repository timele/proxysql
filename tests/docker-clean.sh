#!/bin/bash
docker rmi mysql_0 mysql_1 mysql_2 -f
docker container rm mysql_0 mysql_1 mysql_2 -f

docker container prune -f
docker volume prune -f
docker network prune -f
docker volume prune -f
docker image prune -f 
# docker-compose -f docker-compose.yml up --build
