FROM python:3.11

LABEL authors="2109j"

ADD . .

RUN pip install discord requests python-vlc discord.py[voice] discord.py ffmpeg

CMD [ "python", "./main.py" ]