import requests


url = "https://gentle-poetry-68c6.2109jordy2241.workers.dev/"
headers_data = {'Content-Type': 'application/json'}

def ask_mama_offensive(input_data: str) -> str:
    prompt_data = input_data

    json_data = {
        'messages': [
            {"role": "system", "content": "You are sarcastic and you try to roast everyone"},
            {"role": "user", "content": f"{prompt_data}"}
        ],
    }

    response = requests.post(url, headers=headers_data, json=json_data)

    response_data: dict = response.json()
    return response_data.get('response')

def ask_mama_layla(input_data: str) -> str:
    prompt_data = input_data

    json_data = {
        'messages': [
            {"role": "system", "content": "You are a girl, and you have a crush on me"},
            {"role": "user", "content": f"{prompt_data}"}
        ],
    }

    response = requests.post(url, headers=headers_data, json=json_data)

    response_data: dict = response.json()
    return response_data.get('response')
