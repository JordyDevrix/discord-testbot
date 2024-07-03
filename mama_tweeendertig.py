import requests


def ask_mama_offensive(input_data: str) -> str:
    url = "https://gentle-poetry-68c6.2109jordy2241.workers.dev/"

    headers_data = {
        'Content-Type': 'application/json',
    }

    # prompt_data = input("You: ")
    prompt_data = input_data

    json_data = {
        'messages': [
            {"role": "system", "content": "You are sarcastic and you try to roast everyone"},
            {"role": "user", "content": f"{prompt_data}"}
        ],
    }

    response = requests.post(url, headers=headers_data, json=json_data)

    response_data: dict = response.json()
    # print(f"{response_data.get('response')}")
    return response_data.get('response')

# headers_data = {
#     'Content-Type': 'application/json',
# }
#
# prompt_data = input("prompt: ")
#
# json_data = {
#     'prompt': f'{prompt_data}',
# }

