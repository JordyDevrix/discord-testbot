import requests


def send_graphql_request(url, query, variables=None):
    headers = {"Content-Type": "application/json"}
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    try:
        response_1 = requests.post(url, json=payload, headers=headers)
        response_1.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        return response_1.json()
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return None


def get_jumbo_music():
    graphql_endpoint = "https://jumboradio.playlist-api.deliver.media/graphql"
    print("Fetching Jumbo Radio music...")
    graphql_query = """
    
    query PlayingNowInfos ($id: String) {
        channel(id: $id) {
            id
            name
            services {
            stream_url
            }
            playingnow {
            current {
                metadata {
                artist
                title
                category
                }
                start_time
                duration_ms
            }
            }
        }
    }
"""
    graphql_variables = {"id": "5f5f12559dc7f2001a6f2ae6"}
    try:
        response = send_graphql_request(graphql_endpoint, graphql_query, graphql_variables)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
    print(response)
    if response:
        print(response)
        return response.get("data").get("channel").get("playingnow").get("current").get("metadata")
    else:
        print("Failed to send GraphQL request.")

