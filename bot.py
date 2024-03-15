import time
from lethal_functions import OpenNewQuestion
import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from discord import Interaction
import random
import datetime


def run_discord_bot():
    def has_administrator_permission(ctx):
        return ctx.author.guild_permissions.administrator

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
        async def button1_callback(self, interaction, button):
            print(interaction)
            button.disabled = True  # set button.disabled to True to disable the button
            button.label = "STOP!"  # change the button's label to something else
            # await interaction.response.send_message("STOP! I DON'T LIKE THIS GAME!")
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("STOP! I DON'T LIKE THIS GAME!")

        @discord.ui.button(label="Let's play a game too :D", style=discord.ButtonStyle.primary)
        async def button2_callback(self, interaction, button):
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

    class VerkeerButton(discord.ui.Button):
        def __init__(self, option, ctx):
            self.ctx: commands.Context = ctx
            super().__init__(label=option, style=discord.ButtonStyle.primary)

        async def callback(self, interaction):
            if self.label == self.view.answer:
                await interaction.response.send_message(f"Goedzo {interaction.user.mention}")
            else:
                await interaction.response.send_message(f"{interaction.user.mention} Kut kind, ga leren ofz...")

    class VolgendeButton(discord.ui.Button):
        def __init__(self, option, ctx):
            self.ctx: commands.Context = ctx
            super().__init__(label=option, style=discord.ButtonStyle.green)

        async def callback(self, interaction):
            if self.view.typ == "verkeersborden":
                quest = OpenNewQuestion.get_new_bord()
                question = quest[1]
                picture_name = question["naam"]
                picture_path = discord.File(f"{quest[0]}/{picture_name}.png")
            else:
                quest = OpenNewQuestion.get_new_situatie()
                question = quest[1]
                picture_name = question["naam"]
                picture_path = discord.File(f"{quest[0]}/{picture_name}.jpg")
            vraag = question["vraag"]
            await interaction.response.send_message(file=picture_path,
                                                    content=vraag,
                                                    view=VerkeerView(options=question["options"],
                                                                     answer=question["answer"],
                                                                     ctx=self.ctx,
                                                                     typ=quest[0]))

    class VerkeerView(discord.ui.View):
        def __init__(self, options, answer, ctx, typ):
            super().__init__()
            self.answer = answer
            self.typ = typ
            for option in options:
                try:
                    self.add_item(VerkeerButton(option, ctx))
                except Exception as e:
                    print(e)
            self.add_item(VolgendeButton("Next", ctx))

    @bot.hybrid_command(name="leerborden", description="leer verkeersborden")
    async def leerborden(ctx: commands.Context):
        quest = OpenNewQuestion.get_new_bord()
        question = quest[1]
        picture_name = question["naam"]
        picture_path = discord.File(f"{quest[0]}/{picture_name}.png")
        vraag = question["vraag"]
        await ctx.send(file=picture_path, content=vraag,
                       view=VerkeerView(options=question["options"], answer=question["answer"], ctx=ctx, typ=quest[0]))

    @bot.hybrid_command(name="leersituaties", description="leer verkeerssituaties")
    async def leersituaties(ctx: commands.Context):
        quest = OpenNewQuestion.get_new_situatie()
        question = quest[1]
        picture_name = question["naam"]
        print(picture_name)
        picture_path = discord.File(f"{quest[0]}/{picture_name}.jpg")
        vraag = question["vraag"]
        await ctx.send(file=picture_path, content=f"{vraag} | `{picture_name}`",
                       view=VerkeerView(options=question["options"], answer=question["answer"], ctx=ctx, typ=quest[0]))

    @bot.hybrid_command(name="timeout", description="give a member a timeout")
    @commands.check(has_administrator_permission)
    async def time_out(ctx: commands.Context,
                       member: discord.Member,
                       seconds: int = 0,
                       minutes: int = 0,
                       hours: int = 0,
                       reason=None):
        print(f"{ctx.command} -- {member} -- {reason}")
        duration = datetime.timedelta(seconds=seconds, minutes=minutes, hours=hours, days=0)
        try:
            await member.timeout(duration, reason=reason)
            if reason is None:
                await ctx.send(f"{member.mention} got timed out for {duration.seconds} seconds")
            else:
                await ctx.send(f"{member.mention} got timed out for {duration.seconds} seconds for {reason}")
            await member.send(f"you got timed out for {duration.seconds} seconds in {ctx.guild.name} for {reason}")
        except Exception as e:
            await ctx.send(
                "You cannot kick higherups, even with that shiny new role u got. so cry cry :_(",
                ephemeral=True)
            print(e)

    @time_out.error
    async def time_out_error(ctx: commands.Context, error):
        await ctx.reply("no perms, cry cry :_(", ephemeral=True)

    @bot.hybrid_command(name="kick", description="kick a member from the server")
    @commands.check(has_administrator_permission)
    async def kick(ctx: commands.Context, member: discord.Member, reason=None):
        print(f"{ctx.command} -- {member} -- {commands.bot_has_permissions()}")
        try:
            if reason is None:
                await member.send(f"You have been kicked from {ctx.guild.name}")
            else:
                await member.send(f"You have been kicked from {ctx.guild.name} for {reason}")
            await member.kick(reason=reason)
            if reason is None:
                await ctx.send(f"{member.mention} got kicked from the server")
            else:
                await ctx.send(f"{member.mention} got kicked for {reason}")
        except Exception as e:
            await ctx.send(
                "You cannot kick higherups, even with that shiny new role u got. so cry cry :_(",
                ephemeral=True)
            print(e)

    @kick.error
    async def kick_error(ctx: commands.Context, error):
        await ctx.reply("no perms, cry cry :_(", ephemeral=True)

    @bot.hybrid_command(name="removetimeout", description="remove a member's timeout")
    @commands.check(has_administrator_permission)
    async def un_time_out(ctx: commands.Context, member: discord.Member):
        print(f"{ctx.command} -- {member} -- {commands.bot_has_permissions()}")
        try:
            await member.edit(timed_out_until=None)
            await ctx.send(f"{member.mention}'s timeout got removed")
            await member.send(f"your timeout got removed in {ctx.guild.name}")
        except Exception as e:
            await ctx.send(
                "You cannot kick higherups, even with that shiny new role u got. so cry cry :_(",
                ephemeral=True)
            print(e)

    @un_time_out.error
    async def time_out_error(ctx: commands.Context, error):
        await ctx.reply("no perms, cry cry :_(", ephemeral=True)

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
