FROM tiangolo/uwsgi-nginx-flask:python3.6

ARG projectDir=/app/

ADD requirements.txt ${projectDir}
RUN pip install -r requirements.txt

ADD *.py ${projectDir}

WORKDIR ${projectDir}

EXPOSE 80
