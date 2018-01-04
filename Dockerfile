FROM python:3.6-alpine
#FROM tiangolo/uwsgi-nginx-flask:python3.6

#RUN sed -i -e "s/worker_processes  1;/worker_processes  0;/" /etc/nginx/nginx.conf
#RUN echo "single-interpreter = true" >> uwsgi.ini

ARG projectDir=/app/
WORKDIR ${projectDir}

ADD requirements.txt ${projectDir}
RUN pip install -r requirements.txt

ADD *.py ${projectDir}

EXPOSE 5000
#EXPOSE 80
