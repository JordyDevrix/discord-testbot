FROM python:3.11

LABEL authors="2109j"

ADD . .

RUN pip install discord requests python-vlc discord.py[voice] discord.py ffmpeg

#RUN apt-get update && \
#    apt-get install -y ffmpeg && \
#    ln -s /usr/bin/ffmpeg /usr/local/bin/ffmpeg

RUN chmod +x ffmpeg

CMD [ "python", "./main.py" ]