import discord
import asyncio
from quart import Quart

app = Quart(__name__)
client = discord.Client(intents=discord.Intents.all())

with open("token.txt", "r") as file:
    token: str = file.read()


@app.before_serving
async def before_serving():
    loop = asyncio.get_event_loop()
    await client.login(token)
    loop.create_task(client.connect())


@app.route("/send", methods=["GET"])
async def send_message():
    # wait_until_ready and check for valid connection is missing here
    channel = client.get_channel(1214700522997678157)
    await channel.send('XYZ')
    return 'OK', 200


@app.route("/send/<message>", methods=["GET"])
async def send_specific_message(message):
    # wait_until_ready and check for valid connection is missing here
    channel = client.get_channel(1214700522997678157)
    await channel.send(message)
    return 'OK', 200


app.run(host='0.0.0.0', port=5100)
