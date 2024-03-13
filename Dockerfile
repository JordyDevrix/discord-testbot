FROM python:3.11

LABEL authors="2109j"

ADD . .

RUN pip install discord

CMD [ "python", "./main.py" ]