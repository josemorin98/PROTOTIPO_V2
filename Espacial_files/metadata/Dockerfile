FROM ubuntu:16.04


#install requeriments
RUN apt-get update --fix-missing
RUN     apt install -y software-properties-common
RUN     add-apt-repository -y ppa:ubuntugis/ppa
RUN     apt-get update --fix-missing
RUN     apt-get install -y python-dev
RUN     apt-get install -y  python-pip
RUN     apt-get install -y gdal-bin
RUN     apt-get install -y libgdal-dev
RUN     apt-get install -y python-gdal
RUN    export CPLUS_INCLUDE_PATH=/usr/include/gdal
RUN    export C_INCLUDE_PATH=/usr/include/gdal
RUN pip install --upgrade "pip < 21.0"
RUN pip install flask
RUN pip install requests
RUN pip install utm
RUN pip install pymongo
RUN pip install geopandas

ADD ./app /app
WORKDIR  /app
#RUN pip install -r requirements.txt
EXPOSE 5000
##ENTRYPOINT [ "python", "/app/test.py" ]
ENTRYPOINT [ "python", "/app/main.py" ]
