import json

import postgrest.exceptions
from supabase import create_client, Client

with open("supacredentials.json", "r") as file:
    data: dict = json.load(file)
    url = data.get("url")
    key = data.get("key")

supabase: Client = create_client(url, key)

# supabase.table('server').insert({"server_id": "2", "server_name": "test"}).execute()

# supabase.table('server').update({'server_name': 'Australia'}).eq('id', 1).execute()


def add_new_server():
    pass

def get_role_by_id():
    ...

def get_all_update_channels():
    response = supabase.table('server').select('announce_channel_id').execute()
    print(response.data)
    return response.data


def get_updates_channel(server_id):
    response = supabase.table('server').select('announce_channel_id').eq('server_id', server_id).execute()
    print(response.data[0].get('announce_channel_id'))
    return response.data[0].get('announce_channel_id')


def set_updates_channel(channel_id, server_id, server_name):
    try:
        response = supabase.table('server').select('*').eq('server_id', server_id).execute()

        # checking if the server table already exists and creating if not #
        if len(response.data) == 0:
            supabase.table('server').insert(
                {
                    "server_id": server_id,
                    "server_name": server_name,
                }
            ).execute()

        supabase.table('server').update(
            {
                'announce_channel_id': channel_id
            }
        ).eq('server_id', server_id).execute()
    except Exception as e:
        print(e)
        supabase.table('server').insert(
            {
                "server_id": server_id,
                "server_name": server_name,
            }
        ).execute()

        supabase.table('server').update(
            {
                'announce_channel_id': channel_id
            }
        ).eq('server_id', server_id).execute()


def add_new_chatlog(server_name, server_id, user_id, user_name, message, channel, attachment):
    try:
        supabase.table('chatlogs').insert(
            {
                "server_id": server_id,
                "user_id": user_id,
                "user_name": user_name,
                "message": message,
                "channel_name": channel,
                "attachment": attachment
            }
        ).execute()
    except postgrest.exceptions.APIError:
        supabase.table('server').insert(
            {
                "server_id": server_id,
                "server_name": server_name,
            }
        ).execute()

        supabase.table('chatlogs').insert(
            {
                "server_id": server_id,
                "user_id": user_id,
                "user_name": user_name,
                "message": message,
                "channel_name": channel,
                "attachment": attachment
            }
        ).execute()
