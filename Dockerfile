FROM python:3.6-alpine

ARG projectDir=/app/
WORKDIR ${projectDir}

ADD requirements.txt ${projectDir}
RUN pip install -r requirements.txt

ADD *.py ${projectDir}

EXPOSE 5000
