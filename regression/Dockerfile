FROM python:3.8-slim-buster

#install requeriments
RUN pip install flask
RUN pip install requests
RUN pip install pandas
RUN pip install matplotlib
RUN pip install sklearn
RUN pip install seaborn

COPY ./ /app
WORKDIR  /app
EXPOSE 5000
CMD [ "chmod","775","/app" ]
ENTRYPOINT [ "python3", "/app/app.py"]