#!/bin/sh
docker-compose down
cd loadBalanceGeneric
docker build -t jmorin98/loadbalancer:latest .
docker push jmorin98/loadbalancer:latest
cd ..
cd clustering
docker build -t jmorin98/clustering:latest .
docker push jmorin98/clustering:latest
cd ..
cd regression
docker build -t jmorin98/regression:latest .
docker push jmorin98/regression:latest
cd ..
docker-compose up --build
