#!/bin/sh
docker-compose down
cd loadBalanceGeneric
docker build -t jmorin98/loadbalancer:latest .
docker push jmorin98/loadbalancer:latest
cd ..
cd workerGeneric
docker build -t jmorin98/worker:latest .
docker push jmorin98/worker:latest
cd ..
docker-compose up --build
