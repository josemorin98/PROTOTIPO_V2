#!/bin/sh
docker-compose down
cd loadBalanceGeneric
docker build -t jmorin98/loadbalancer:latest .
docker push jmorin98/loadbalancer:latest
# cd ..
# cd clustering
# docker build -t jmorin98/clustering:latest .
# docker push jmorin98/clustering:latest
cd ..
cd Tests
docker build -t jmorin98/test:latest .
docker push jmorin98/test:latest
cd ..
    # cd Map_Mexico
    # docker build -t jmorin98/mapamx:latest .
    # docker push jmorin98/mapamx:latest
# cd ..
# cd regression
# docker build -t jmorin98/regression:latest .
# docker push jmorin98/regression:latest
# cd ..
cd correlation
docker build -t jmorin98/correlation:latest .
docker push jmorin98/correlation:latest
cd ..
# cd conteo
# docker build -t jmorin98/conteo:latest .
# docker push jmorin98/conteo:latest
# cd ..
docker-compose up --build
