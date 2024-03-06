import discord
from discord.ext import commands
from discord import Interaction
import random


def run_discord_bot():

    with open("token.txt", "r") as file:
        token: str = file.read()

    bot = commands.Bot(command_prefix=",", intents=discord.Intents.all())

    @bot.hybrid_command()
    async def ping(ctx: commands.Context):
        await ctx.send("pong")

    @bot.hybrid_command()
    async def dm(ctx: commands.Context):
        choose: str = random.choice(["sup?", "whats good?", "what ya need?"])
        await ctx.author.send(choose)
        await ctx.send("watch yo dm's")

    class MyView(discord.ui.View):  # Create a class called MyView that subclasses discord.ui.View
        @discord.ui.button(label="Let's play a game :D", style=discord.ButtonStyle.primary)
        async def button_callback(self, interaction, button):
            print(interaction)
            button.disabled = True  # set button.disabled to True to disable the button
            button.label = "STOP!"  # change the button's label to something else
            await interaction.response.send_message("STOP! I DON'T LIKE THIS GAME!")
            # await interaction.response.edit_message(view=self)

    @bot.hybrid_command(name="test", description="testing a discord bot")
    async def test(ctx: commands.Context):
        print(ctx)
        await ctx.send("succes!", view=MyView())

    @bot.hybrid_command()
    async def hello(ctx):
        await ctx.send("krijg kanker!")

    @bot.event
    async def on_ready():
        print("bot running")
        await bot.tree.sync()
        await bot.change_presence(activity=discord.activity.Game(name="nick aan het voeren"))

    bot.run(token)
