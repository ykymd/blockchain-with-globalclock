FROM tiangolo/uwsgi-nginx-flask:python3.6

ARG projectDir=/app/

ADD requirements.txt ${projectDir}
ADD *.py ${projectDir}

WORKDIR ${projectDir}
RUN pip install -r requirements.txt

EXPOSE 80
