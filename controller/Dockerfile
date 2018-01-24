FROM python:3.6-alpine

RUN pip install requests

RUN apk --update add curl

ADD *.py ./

CMD [ "python", "-u", "randomlinker.py" ]
