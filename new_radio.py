import vlc


def play_new_radio(choice: int):
    url_radio_538 = "https://playerservices.streamtheworld.com/api/livestream-redirect/RADIO538AAC.aac"
    url_jumbo_radio = "https://streams.automates.media/jumboradio"

    if choice == 2:
        url = url_jumbo_radio
    else:
        url = url_radio_538

    return url

    # p = vlc.MediaPlayer(url)
    #
    # while True:
    #     p.play()
    #     i = input("x to quit")
