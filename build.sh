#!/bin/sh
docker-compose down
cd loadBalanceGeneric
docker build -t jmorin98/lb_generic:latest .
docker push jmorin98/loadBalanceGeneric:latest
cd ..
cd workerGeneric
docker build -t jmorin98/workers:latest .
docker push jmorin98/workers:latest
cd ..
docker-compose up --build