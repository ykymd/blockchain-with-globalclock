#FROM python:3.6-alpine
FROM tiangolo/uwsgi-nginx-flask:python3.6

ARG projectDir=/app/
WORKDIR ${projectDir}

# mongodb
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
RUN echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.4.list
RUN apt-get update
RUN apt-get install -y mongodb
#RUN mongod --fork --dbpath /var/lib/mongodb --logpath /var/log/mongodb.log

ADD requirements.txt ${projectDir}
RUN pip install -r requirements.txt

ADD *.py ${projectDir}

EXPOSE 80

#ENTRYPOINT ["mongod", "--fork", "--dbpath", "/var/lib/mongodb", "--logpath", "/var/log/mongodb.log"]
