import json
import random


class PresenceChange:
    def get_presence_state(self) -> str:
        ...


class OpenNewQuestion:

    @staticmethod
    def get_new_bord() -> list:
        with open("verkeersborden.json", "r") as f:
            data = json.load(f)
            maxi = len(data["my_list"]) - 1
            question = data["my_list"][random.randint(0, maxi)]
            print(maxi)
            return ["verkeersborden", question]

    @staticmethod
    def get_new_situatie() -> list:
        with open("verkeerssituaties.json", "r") as f:
            data = json.load(f)
            maxi = len(data["my_list"]) - 1
            question = data["my_list"][random.randint(0, maxi)]
            print(maxi)
            return ["verkeerssituaties", question]
