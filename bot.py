import discord
from discord.ext import commands, tasks
from discord import Interaction
import random

import lethal_functions


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
            # await interaction.response.send_message("STOP! I DON'T LIKE THIS GAME!")
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("STOP! I DON'T LIKE THIS GAME!")

    @bot.hybrid_command(name="test", description="testing a discord bot")
    async def test(ctx: commands.Context):
        print(ctx)
        await ctx.send("succes!", view=MyView())

    @bot.hybrid_command(name="kick", description="kick someone")
    async def hello(ctx: commands.Context):
        print(ctx.guild)
        for guild in bot.guilds:
            print(f"{guild.id} -- {guild.name}")
            if guild.id == 1214700522133782528:
                for member in guild.members:
                    # print(member)
                    if str(member.id) == "732294186186965032":
                        print("gevonden")
                        await member.kick()

        await ctx.send("nothing")

    @bot.event
    async def on_ready():
        print("bot running")
        change_status.start()
        await bot.tree.sync()

    @tasks.loop(seconds=10)
    async def change_status():
        # print("10 seconds passed")
        await bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=random.choice(["hoe elio mijn spullen steelt",
                                "hoe stefan kinderen verzameld",
                                "bas requirement engineering uitleggen",
                                "videocolleges",
                                "hoe ronald huilt als je een uurtje eerder weggaat",
                                "hoe michiel maurice bedreigd",
                                "kevin's hairline recede",
                                "jordy's dad getting milk"
                                ]),
            details="Elio steelt weereens mijn spullen -_-",
            description="Elio steelt weereens mijn spullen -_-"
        )
        )

    bot.run(token)

