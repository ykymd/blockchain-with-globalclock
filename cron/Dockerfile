FROM python:3.6

RUN pip install requests

ADD *.py ./
RUN echo '*/1 * * * * root python mine.py' >> /etc/crontab
CMD ["cron", "-f"]
