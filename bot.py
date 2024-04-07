import asyncio
import platform
import time

import verkeersopgaven
from lethal_functions import OpenNewQuestion
import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from discord import Interaction
import random
import datetime
import jumboreq
from discord import FFmpegPCMAudio


def run_discord_bot():
    def has_administrator_permission(ctx):
        return ctx.author.guild_permissions.administrator

    with open("token.txt", "r") as file:
        token: str = file.read()

    bot = commands.Bot(command_prefix=",", intents=discord.Intents.all())

    @bot.hybrid_command()
    async def ping(ctx: commands.Context):
        await ctx.send("pong")

    @bot.hybrid_command(name="stopradio", description="stop music")
    async def ping(ctx: commands.Context):
        try:
            print(ctx.guild.voice_client.channel)
            await ctx.guild.voice_client.disconnect(force=True)
            await ctx.send("**Voice channel verlaten**")
        except Exception as e:
            print(e)
            await ctx.send("**Bot is niet aanwezig in een voice channel**")

    @bot.hybrid_command(name="playradio", description="play music")
    async def play_jumbo_radio(ctx: commands.Context):
        try:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()
            if platform.system() == "Windows":
                voice_client.play(FFmpegPCMAudio(
                    executable="ffmpeg-2024-03-18-git-a32f75d6e2-essentials_build/bin/ffmpeg.exe",
                    source="https://playerservices.streamtheworld.com/api/livestream-redirect/JUMBORADIOAAC.aac"
                ))
            else:
                voice_client.play(FFmpegPCMAudio(
                    executable="ffmpeg",
                    source="https://playerservices.streamtheworld.com/api/livestream-redirect/JUMBORADIOAAC.aac"
                ))
            await channel.guild.me.edit(deafen=True)
            await channel.guild.me.edit(mute=False)
            response: dict = jumboreq.get_jumbo_music()
            if response.get("artist") == "Commercial":
                await ctx.send(f"Playing **{response.get('artist')}**")
            else:
                await ctx.send(f"Playing **{response.get('artist')} - {response.get('title')}**")
        except AttributeError as e:
            if e.name == "channel":
                await ctx.send(f"**Join eerst een Voice Channel om muziek af te spelen**")
            else:
                await ctx.send(f"**Het is niet mogelijk om in DM muziek af te spelen**")
        except Exception as e:
            await ctx.send("**Er is niemand aanwezig in een voicechannel**")
            print(e)
            await ctx.send(f"{e}")

    @bot.hybrid_command(name="dm", description="Verstuurd je een DM")
    async def dm(ctx: commands.Context):
        choose: str = random.choice(["Yo?", "Hoe kan ik je helpen?", "Iets nodig?"])
        await ctx.author.send(choose)
        await ctx.send("Bekijk je DM's")

    @bot.hybrid_command(name="jumboradio", description="gives the current song playing on jumboradio")
    async def get_jumbo_radio(ctx: commands.Context):
        response: dict = jumboreq.get_jumbo_music()
        if response.get("artist") == "Commercial":
            await ctx.send(f"Er speelt momenteel geen muziek: **{response.get('artist')}**")
        else:
            await ctx.send(f"Muziek op jumbo radio: **{response.get('artist')} - {response.get('title')}**")

# CBR verkeersvragen #

    @bot.hybrid_command(name="leerborden", description="leer verkeersborden")
    async def leerborden(ctx: commands.Context):
        quest = OpenNewQuestion.get_new_bord()
        question = quest[1]
        picture_name = question["naam"]
        picture_path = discord.File(f"{quest[0]}/{picture_name}.png", filename="output.png")
        vraag = question["vraag"]
        embed = discord.Embed(title="Borden", color=discord.Color(int('ffc800', 16)))
        embed.add_field(name=f"{vraag} | `{picture_name}`", value="click op het juiste antwoord", inline=True)
        embed.set_image(url=f"attachment://output.png")
        await ctx.send(
            embed=embed,
            file=picture_path,
            view=verkeersopgaven.VerkeerView(options=question["options"], answer=question["answer"], ctx=ctx, typ=quest[0])
        )
    @bot.hybrid_command(name="leersituaties", description="leer verkeerssituaties")
    async def leersituaties(ctx: commands.Context):
        quest = OpenNewQuestion.get_new_situatie()
        question = quest[1]
        picture_name = question["naam"]
        print(picture_name)
        picture_path = discord.File(f"{quest[0]}/{picture_name}.jpg", filename="output.png")
        vraag = question["vraag"]

        embed = discord.Embed(title="Situaties", color=discord.Color(int('ffc800', 16)))
        embed.add_field(name=f"{vraag} | `{picture_name}`", value="click op het juiste antwoord", inline=True)
        embed.set_image(url=f"attachment://output.png")
        await ctx.send(
            embed=embed,
            file=picture_path,
            view=verkeersopgaven.VerkeerView(options=question["options"], answer=question["answer"], ctx=ctx, typ=quest[0])
        )

# Moderation functies #

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
        # print(f"{ctx.command} -- {member} -- {commands.bot_has_permissions()}")
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

# Auto disconnect discord bot from voicechannel and change RPC #

    @tasks.loop(seconds=10)
    async def change_status():
        for guild in bot.guilds:
            for channel in guild.voice_channels:
                if len(channel.members) == 1:
                    try:
                        for member in channel.members:
                            if str(member.id) == "1214671466780565575":
                                print(len(channel.members),
                                      "in",
                                      guild.name,
                                      "bot connected to",
                                      guild.voice_client.channel,
                                      channel.members
                                      )
                                await guild.voice_client.disconnect(force=True)
                    except Exception as e:
                        print(f"{e}\nbot not connected to any channel")

        # print("10 seconds passed")
        await bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=random.choice(["laatste aanbiedingen",
                                "de jumbo discord",
                                "de radio DJ's"
                                ])
        )
        )

    bot.run(token)
