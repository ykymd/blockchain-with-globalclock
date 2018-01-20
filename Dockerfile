#FROM python:3.6-alpine
FROM tiangolo/uwsgi-nginx-flask:python3.6

ARG projectDir=/app/
WORKDIR ${projectDir}

# ソースコード変更済みのパッケージを追加
ADD tinydb ${projectDir}/tinydb

ADD requirements.txt ${projectDir}
RUN pip install -r requirements.txt

ADD *.py ${projectDir}

#EXPOSE 5000
EXPOSE 80
