from pypresence import Presence
import random

import lethal_functions


def update_presence():
    rpc = Presence("")
    rpc.connect()

    while True:
        rpc.update(
            state="Watching hoe elio mijn spullen steelt",
            large_image="walter_white"
        )


update_presence()
