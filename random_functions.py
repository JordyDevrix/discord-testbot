import requests


def get_number(number):
    url = 'http://numbersapi.com/'
    response = requests.get(f"{url}{number}")
    # print(f"{response.text} + {number}")

    return response.text


def get_random_dog():
    response = requests.get("https://dog.ceo/api/breeds/image/random")

    # print(response.json().get('message'))

    return response.json().get('message')


def get_random_cat():
    response = requests.get("https://api.thecatapi.com/v1/images/search")

    # print(response.json()[0].get('url'))

    return response.json()[0].get('url')


def get_random_activity():
    response = requests.get("https://www.boredapi.com/api/activity")

    # print(f"{response.json().get('type')}: {response.json().get('activity')}")

    return f"**{response.json().get('type').capitalize()}**: {response.json().get('activity')}"