import platform

import vlc
import os
import time

url = 'https://playerservices.streamtheworld.com/api/livestream-redirect/JUMBORADIOAAC.aac'

# define VLC instance
instance = vlc.Instance('--input-repeat=-1', '--fullscreen')

# Define VLC player
player = instance.media_player_new()

# Define VLC media
media = instance.media_new(url)

# Set player media
player.set_media(media)

# Play the media
player.play()

while True:
    print(platform.system())
    i = input("x to quit")
    if i == "x":
        player.stop()
        exit(0)
