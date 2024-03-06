from pypresence import Presence
import random

import lethal_functions


def update_presence():
    rpc = Presence("1214671466780565575")
    rpc.connect()

    while True:
        rpc.update(
            state="Watching hoe elio mijn spullen steelt",
            large_image="walter_white"
        )


update_presence()
