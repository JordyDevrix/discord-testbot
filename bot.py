import discord
from discord.ext import commands
from discord import Interaction


def run_discord_bot():

    with open("token.txt", "r") as file:
        token: str = file.read()

    bot = commands.Bot(command_prefix=",", intents=discord.Intents.all())

    @bot.hybrid_command()
    async def ping(ctx: commands.Context):
        await ctx.send("pong")

    @bot.hybrid_command()
    async def dm(interaction: Interaction):
        user = await interaction.user.create_dm()
        await user.send("help")

    @bot.hybrid_command(name="test", description="testing a discord bot")
    async def test(ctx: commands.Context):
        await ctx.send("succes!")

    @bot.hybrid_command()
    async def hello(ctx):
        await ctx.send("krijg kanker!")

    @bot.event
    async def on_ready():
        print("bot running")
        await bot.tree.sync()
        await bot.change_presence(activity=discord.activity.Game(name="nick aan het voeren"))

    bot.run(token)
