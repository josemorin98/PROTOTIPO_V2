FROM python:3.8-slim-buster

#install requeriments
RUN pip install flask
RUN pip install requests
RUN pip install pandas

COPY ./ /app
WORKDIR  /app
EXPOSE 5000
CMD [ "chmod","775","/app" ]
ENTRYPOINT [ "python3", "/app/app.py"]