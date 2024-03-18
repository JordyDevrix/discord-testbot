FROM python:3.11

LABEL authors="2109j"

ADD . .

ADD ffmpeg-2024-03-18-git-a32f75d6e2-essentials_build/bin/ffmpeg.exe /usr/local/bin/ffmpeg

RUN chmod +x /usr/local/bin/ffmpeg

RUN pip install discord requests python-vlc discord.py[voice] discord.py ffmpeg

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    ln -s /usr/bin/ffmpeg /usr/local/bin/ffmpeg


CMD [ "python", "./main.py" ]