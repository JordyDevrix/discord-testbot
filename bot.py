import datetime
import json
import platform
import random
import new_radio

from discord.app_commands import Choice
from openai import OpenAI

import mama_tweeendertig
import random_functions
import asyncio
import discord
from discord import FFmpegPCMAudio, app_commands
from discord.ext import commands, tasks
from discord.ext.commands import CheckFailure

import jumboreq
import supabase_connector
import tts_function
import verkeersopgaven
from lethal_functions import OpenNewQuestion
from permission_check import *


def run_discord_bot():
    with open("supacredentials.json", "r") as file:
        data = json.load(file)
        api_key = data.get("GPT_KEY")
        client = OpenAI(api_key=api_key)

    with open("token.txt", "r") as file:
        token: str = file.read()

    bot = commands.Bot(command_prefix=",", intents=discord.Intents.all())
    intent = discord.Intents.default()
    intent.members = True
    intent.message_content = True

    @bot.event
    async def on_member_join(member: discord.Member):
        server_id = member.guild.id
        current_join_roles: list = supabase_connector.get_on_join_roles(server_id)[0].get("on_join_roles")
        for role_id in current_join_roles:
            role = discord.utils.get(member.guild.roles, id=role_id)
            await member.add_roles(role)

    def create_ai_message(prompt, models, msg):
        if models.value == "a":
            try:
                model = "gpt-4o"
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": msg}
                    ]
                )
                return f"`q:'{msg}' model:{model}`\n{response.choices[0].message.content}"
            except Exception as e:
                print(e)
                return Exception

        elif models.value == "b":
            try:
                model = "llama3"
                response = mama_tweeendertig.ask_mama_offensive(msg)
                return f"`q='{msg}' model:{model}`\n{response}"
            except Exception as e:
                print(e)
                return Exception

        elif models.value == "c":
            try:
                model = "gpt-4-turbo"
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": msg}
                    ]
                )
                return f"`q:'{msg}' model:{model}`\n{response.choices[0].message.content}"
            except Exception as e:
                print(e)
                return Exception

        elif models.value == "d":
            try:
                model = "llama3"
                response = mama_tweeendertig.ask_mama_layla(msg)
                return f"`q='{msg}' model:{model}`\n{response}"
            except Exception as e:
                print(e)
                return Exception

        elif models.value == "e":
            try:
                model = "llama3"
                response = mama_tweeendertig.ask_general(msg)
                return f"`q='{msg}' model:{model}`\n{response}"
            except Exception as e:
                print(e)
                return Exception

        elif models.value == "f":
            try:
                model = "o1-preview"
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": msg}
                    ]
                )
                return f"`q:'{msg}' model:{model}`\n{response.choices[0].message.content}"
            except Exception as e:
                print(e)
                return Exception

    @bot.hybrid_command(name="chat", description="Use the bot's AI functionality")
    @commands.guild_only()
    @app_commands.choices(models=[
        app_commands.Choice(name="Speed (GPT-4-TURBO)", value="a"),
        app_commands.Choice(name="Offensive (llama-3)", value="b"),
        app_commands.Choice(name="Smart (GPT-4o)", value="c"),
        app_commands.Choice(name="Layla (llama-3)", value="d"),
        app_commands.Choice(name="General (llama-3)", value="e"),
        app_commands.Choice(name="Reasoning (GPT-o1-preview)", value="f"),
    ])
    async def chat(ctx: commands.Context, msg, models: app_commands.Choice[str] = None):
        if models is None:
            models = app_commands.Choice(name="Smart (GPT-40)", value="c")

        msg_edit = await ctx.reply("<a:jumbotloadingemoji:1293627455537680446> Generating response...")
        print(models.value)

        response = ""
        try:
            response = await asyncio.to_thread(create_ai_message, msg, models, msg)
            await msg_edit.edit(content=response)
        except discord.errors.HTTPException as e:
            print(e)
            await msg_edit.edit(content=f"Response too long ({len(response)} characters. Max 2000)")
        except Exception as e:
            print(e)
            await msg_edit.edit(content=f"Something went wrong {e}")

    def create_ai_image(prompt, model):
        response = client.images.generate(
            model=model,
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return image_url

    @bot.hybrid_command(name="imagen", description="Use the bot's AI image generation functionality")
    @commands.guild_only()
    async def imagen(ctx: commands.Context, prompt: str, hurt_my_wallet: bool = False):
        if hurt_my_wallet:
            model = "dall-e-3"
        else:
            model = "dall-e-2"
        await ctx.send(f"<a:jumbotloadingemoji:1293627455537680446> Generating {prompt}...")
        try:
            image = await asyncio.to_thread(create_ai_image, prompt, model)
            await ctx.channel.send(image)
        except Exception as e:
            print(e)
            await ctx.send("Something went wrong")

    @bot.hybrid_command(
        name="jumbothelp",
        description="This command will send a link in the chat to the jumbot website",
        usage="use by entering /help in the chat",
        brief="Help command"
    )
    async def help_command(ctx: commands.Context):
        await ctx.send(f"https://jumbot.jordydevrix.com/")

    @bot.hybrid_command(name="servercount", description="See the amount of servers jumbot is in")
    async def server_count(ctx: commands.Context):
        server_len = str(len(bot.guilds))
        for guild in bot.guilds:
            print(guild.name)
        await ctx.send(server_len)

    @bot.hybrid_command(name="google", description="Use qooqle to search something for someone")
    async def ik_google_het_wel(ctx: commands.Context, query):
        te_googlen = query.strip().replace(' ', '+')
        await ctx.send(f"https://www.qooqle.nl/?q={te_googlen}")

    @bot.hybrid_command(name="random_activity", description="Get a random activity when you're bored")
    async def random_activity(ctx: commands.Context):
        activity = random_functions.get_random_activity()
        await ctx.send(activity)

    @bot.hybrid_command(name="number_fact", description="Get a fact about a number")
    async def number_fact(ctx: commands.Context, number=None):
        if number is None:
            number = random.randint(0, 256)
        fact = random_functions.get_number(number)
        await ctx.send(fact)

    @bot.hybrid_command(name="join_roles", description="Remove a join role")
    @commands.guild_only()
    @commands.check(has_manage_server_permission)
    async def join_roles(ctx: commands.Context):
        server_id = ctx.guild.id
        join_role_list: list = supabase_connector.get_on_join_roles(server_id)[0].get("on_join_roles")
        message = ""
        if len(join_role_list) == 0:
            await ctx.send("No roles found")
        else:
            for idx, role in enumerate(join_role_list):
                message += f"{idx + 1} - {discord.utils.get(ctx.guild.roles, id=role)}\n"

            await ctx.send(f"Roles found:\n{message}")

    @bot.hybrid_command(name="remove_join_role", description="Remove a join role")
    @commands.guild_only()
    @commands.check(has_manage_server_permission)
    async def remove_join_role(ctx: commands.Context, role: discord.Role):
        server_id = ctx.guild.id
        roler = role
        server_name = ctx.guild.name
        role_to_remove = role.id
        current_join_roles: list = supabase_connector.get_on_join_roles(server_id)[0].get("on_join_roles")

        role_found = False
        for role in current_join_roles:
            if role == role_to_remove:
                role_found = True

        if role_found:
            current_join_roles.remove(role_to_remove)
            await ctx.send(f"Removing role **{roler.name}**")
        else:
            await ctx.send("Role not found")

        supabase_connector.set_on_join_roles(server_id, server_name, current_join_roles)

    @remove_join_role.error
    async def remove_join_role_error(ctx: commands.Context, error):
        if isinstance(error, PermissionError):
            await ctx.reply("no perms, cry cry :_(", ephemeral=True)
        else:
            await ctx.send("Something went wrong try again later or contact the developer")

    @bot.hybrid_command(name="set_join_role", description="Set a role a user gets when they join the server")
    @commands.guild_only()
    @commands.check(has_manage_server_permission)
    async def set_join_role(ctx: commands.Context, role: discord.Role):
        server_id = ctx.guild.id
        server_name = ctx.guild.name
        role_to_set = role.id
        current_join_roles: list = supabase_connector.get_on_join_roles(server_id)[0].get("on_join_roles")

        role_added = False
        for role in current_join_roles:
            if role == role_to_set:
                role_added = True

        if role_added:
            await ctx.send("Role has already been added")
        else:
            current_join_roles.append(role_to_set)
            await ctx.send("Added role")

        supabase_connector.set_on_join_roles(server_id, server_name, current_join_roles)

    @set_join_role.error
    async def set_join_role_error(ctx: commands.Context, error):
        if isinstance(error, PermissionError):
            await ctx.reply("no perms, cry cry :_(", ephemeral=True)
        else:
            await ctx.send("Something went wrong try again later or contact the developer")

    @bot.hybrid_command(name="set_updates_channel", description="sets a specific channel for updates")
    @commands.guild_only()
    @commands.check(has_administrator_permission)
    async def set_updates_channel(ctx: commands.Context, channel):
        for server_channel in ctx.guild.channels:
            if str(server_channel.id) in str(channel):
                print(server_channel.id, channel)
                supabase_connector.set_updates_channel(server_channel.id, ctx.guild.id, ctx.guild.name)
                await ctx.send(f"Channel: <#{server_channel.id}> set for bot announcements")

    @set_updates_channel.error
    async def set_updates_channel_error(ctx: commands.Context, error):
        if isinstance(error, PermissionError):
            await ctx.reply("no perms, cry cry :_(", ephemeral=True)
        else:
            await ctx.send("Something went wrong try again later or contact the developer")

    # @bot.hybrid_command(name="deletelog", description="Show all the deleted messages from your server")
    # @commands.guild_only()
    # @commands.check(has_administrator_permission)
    # async def deletelog(ctx: commands.Context, amount=1):
    #     server_id = ctx.guild.id
    #     messages = supabase_connector.get_deleted_messages(server_id)
    #     messages_sorted = sorted(messages, key=lambda x: x['id'])
    #     messages_sorted.reverse()
    #     if len(messages) == 0:
    #         await ctx.send("No deleted messages found")
    #     else:
    #         if amount > 10:
    #             await ctx.send("Please do not request more then 10 messages")
    #         else:
    #             if amount == 1:
    #                 await ctx.send(f"Sending last message")
    #             else:
    #                 await ctx.send(f"Sending last {amount} messages")
    #             for i in range(amount):
    #                 msg: dict = messages_sorted[i]
    #                 msg_time = msg.get('message_time').split('.')[0].split('T')
    #                 await ctx.send(f"`ID:{msg.get('id')} | {msg_time[0]} {msg_time[1]} | {msg.get('user_name')}`\n"
    #                                f"{msg.get('message')}\n"
    #                                f"{msg.get('attachment')}")
    #
    # @deletelog.error
    # async def deletelog_error(ctx: commands.Context, error):
    #     if isinstance(error, PermissionError):
    #         await ctx.reply("no perms, cry cry :_(", ephemeral=True)
    #     else:
    #         await ctx.send("Something went wrong try again later or contact the developer")

    @bot.hybrid_command(name="announce", description="announce something")
    @commands.guild_only()
    @commands.check(has_administrator_permission)
    async def announce(ctx: commands.Context,
                       title=None,
                       content=None,
                       links=None,
                       mention_everyone=False,
                       global_announcement=False
                       ):
        announcement_parts = [title, content, links]
        if global_announcement:
            if str(ctx.author.id) == "495328668105703426":
                data = supabase_connector.get_all_update_channels()
                succescount = 0
                for server in data:
                    try:
                        channel_id = server.get('announce_channel_id')
                        channel = bot.get_channel(channel_id)
                        if channel_id is None:
                            continue
                        else:
                            announcement = ""
                            for part in announcement_parts:
                                if part is None:
                                    pass
                                else:
                                    announcement += f"{part}\n"
                            if mention_everyone:
                                announcement += f"{ctx.guild.default_role}"
                            await channel.send(announcement)
                            succescount += 1
                    except Exception as e:
                        print(e)
                await ctx.send(f"Announcement made by {ctx.author.mention} to {succescount} / {len(data)} servers")
            else:
                await ctx.send("You're not one of the bot developers", ephemeral=True)
        else:
            channel_id = supabase_connector.get_updates_channel(ctx.guild.id)
            channel = ctx.guild.get_channel(channel_id)
            announcement = ""
            for part in announcement_parts:
                if part is None:
                    pass
                else:
                    announcement += f"{part}\n"
            if mention_everyone:
                announcement += f"{ctx.guild.default_role}"

            await channel.send(announcement)
            await ctx.send(f"Announcement made by {ctx.author.mention}")

    @announce.error
    async def announce_error(ctx: commands.Context, error):
        if isinstance(error, PermissionError):
            await ctx.reply("no perms, cry cry :_(", ephemeral=True)
        else:
            await ctx.send("Something went wrong try again later or contact the developer")

    # @bot.hybrid_command()
    # async def ping(ctx: commands.Context):
    #     await ctx.send("pong")

    @bot.hybrid_command(name="stopradio", description="stop music")
    @commands.guild_only()
    async def stop_jumbo_radio(ctx: commands.Context):
        try:
            for idx, voice_channel in enumerate(ctx.guild.voice_channels):
                removed = False
                if ctx.author in voice_channel.members:
                    print(ctx.guild.voice_client.channel)
                    await ctx.guild.voice_client.disconnect(force=True)
                    await ctx.send("**Voice channel verlaten**")
                #     removed = True
                # if len(ctx.guild.voice_channels) == idx + 1 and not removed:
                #     await ctx.send("**Je moet eerst een voicechannel joinen**")
        except Exception as e:
            print(e)
            await ctx.send("**Bot is niet aanwezig in een voice channel**")

    radio_channels = [
        app_commands.Choice(name="Radio 538", value="https://playerservices.streamtheworld.com/api/livestream-redirect/RADIO538AAC.aac"),
        app_commands.Choice(name="Radio 538 TOP 50", value="https://playerservices.streamtheworld.com/api/livestream-redirect/TLPSTR01AAC.aac"),
        app_commands.Choice(name="Jumbo Radio", value="https://streams.automates.media/jumboradio"),
        app_commands.Choice(name="Qmusic", value="https://stream.qmusic.nl/qmusic/aac"),
        app_commands.Choice(name="Qmusic (Non stop)", value="https://stream.qmusic.nl/nonstop/aac"),
        app_commands.Choice(name="Sky Radio", value="https://www.mp3streams.nl/zender/skyradio/stream/8-mp3-128"),
        app_commands.Choice(name="Slam", value="https://25653.live.streamtheworld.com/SLAM_AAC.aac"),
    ]

    @bot.hybrid_command(name="radio", description="play music")
    @commands.guild_only()
    @app_commands.choices(channels=radio_channels)
    async def play_new_radio(ctx: commands.Context, channels: app_commands.Choice[str] = None):

        if channels is None:
            # Choose a random radio station
            channels = random.choice(radio_channels)

        choice: str = channels.value
        radio_name: str = channels.name
        print(choice)

        try:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()
            if platform.system() == "Windows":
                voice_client.play(FFmpegPCMAudio(
                    executable="ffmpeg-2024-03-18-git-a32f75d6e2-essentials_build/bin/ffmpeg.exe",
                    source=choice
                ))
            else:
                voice_client.play(FFmpegPCMAudio(
                    executable="ffmpeg",
                    source=choice
                ))
            await channel.guild.me.edit(deafen=True)
            await channel.guild.me.edit(mute=False)
            await ctx.send(f"Playing **{radio_name}**")
        except AttributeError as e:
            if e.name == "channel":
                await ctx.send(f"**Join eerst een Voice Channel om muziek af te spelen**")
            else:
                await ctx.send(f"**Het is niet mogelijk om in DM muziek af te spelen**")

    @bot.hybrid_command(name="playradio", description="play music")
    @commands.guild_only()
    async def play_jumbo_radio(ctx: commands.Context):
        try:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()
            if platform.system() == "Windows":
                voice_client.play(FFmpegPCMAudio(
                    executable="ffmpeg-2024-03-18-git-a32f75d6e2-essentials_build/bin/ffmpeg.exe",
                    source="https://streams.automates.media/jumboradio"
                ))
            else:
                voice_client.play(FFmpegPCMAudio(
                    executable="ffmpeg",
                    source="https://streams.automates.media/jumboradio"
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
            print(e)
            await ctx.send(f"**{e}**")

    @bot.hybrid_command(name="dm", description="Verstuurd je een DM")
    @commands.guild_only()
    async def dm(ctx: commands.Context):
        choose: str = random.choice(["Yo?", "Hoe kan ik je helpen?", "Iets nodig?"])
        await ctx.author.send(choose)
        await ctx.send("Bekijk je DM's")

    @bot.hybrid_command(name="jumboradio", description="gives the current song playing on jumboradio")
    async def get_jumbo_radio(ctx: commands.Context):
        response: dict = jumboreq.get_jumbo_music()
        artist: str = response.get("artist")
        if artist.lower().strip() == "commercial" or artist.lower().strip() == "reclame":
            await ctx.send(f"Er speelt momenteel geen muziek: **{response.get('artist')}**")
        else:
            await ctx.send(f"Muziek op jumbo radio: **{response.get('artist')} - {response.get('title')}**")

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
            view=verkeersopgaven.VerkeerView(options=question["options"], answer=question["answer"], ctx=ctx,
                                             typ=quest[0])
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
            view=verkeersopgaven.VerkeerView(options=question["options"], answer=question["answer"], ctx=ctx,
                                             typ=quest[0])
        )

    @bot.hybrid_command(name="timeout", description="give a member a timeout")
    @commands.guild_only()
    @commands.check(has_timeout_permission)
    async def time_out(ctx: commands.Context,
                       member: discord.Member,
                       seconds: int = 0,
                       minutes: int = 0,
                       hours: int = 0,
                       reason=None):
        print(f"{ctx.command} -- {member} -- {reason}")
        if ctx.author.id == member.id:
            await ctx.send("You cannot give yourself a timeout")
        else:
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
                    "You cannot timeout members with same or higher permissions",
                    ephemeral=True)
                print(e)

    @time_out.error
    async def time_out_error(ctx: commands.Context, error: discord.ext.commands.errors.CheckFailure):
        print(error)
        if isinstance(error, (PermissionError, CheckFailure)):
            await ctx.reply("no perms, cry cry :_(", ephemeral=True)
        else:
            await ctx.send("Something went wrong try again later or contact the developer")

    @bot.hybrid_command(name="removetimeout", description="remove a member's timeout")
    @commands.guild_only()
    @commands.check(has_untimeout_permission)
    async def un_time_out(ctx: commands.Context, member: discord.Member):
        try:
            await member.edit(timed_out_until=None)
            await ctx.send(f"{member.mention}'s timeout got removed")
            await member.send(f"your timeout got removed in {ctx.guild.name}")
        except Exception as e:
            await ctx.send(
                "You cannot remove timeouts without the correct permission",
                ephemeral=True)
            print(e)

    @un_time_out.error
    async def time_out_error(ctx: commands.Context, error):
        print(error)
        if isinstance(error, (PermissionError, CheckFailure)):
            await ctx.reply("no perms, cry cry :_(", ephemeral=True)
        else:
            await ctx.send("Something went wrong try again later or contact the developer")

    def fetch_servers():
        supabase_connector.fetch_servers(bot.guilds)
        return

    @bot.event
    async def on_ready():
        print("bot running")
        try:
            fetch_servers()
        except Exception as e:
            print(f"Fetching servers failed: {e}")
        change_status.start()
        await bot.tree.sync()

    # Auto disconnect discord bot from voicechannel and change RPC #

    # @bot.event
    # async def on_message_delete(message: discord.Message):
    #     attachmentlist = ""
    #     for idx, attachment in enumerate(message.attachments):
    #         attachmentlist += f"{attachment.url}\n"
    #
    #     deleter = ""
    #     async for entry in message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
    #         deleter = entry.user
    #
    #     try:
    #         if supabase_connector.get_deletelog_permission(message.guild.id)[0].get('deletelog'):
    #             supabase_connector.add_new_chatlog(
    #                 message.guild.name,
    #                 message.guild.id,
    #                 message.author.id,
    #                 message.author.name,
    #                 message.content,
    #                 message.channel.name,
    #                 attachmentlist,
    #                 deleter.id
    #             )
    #     except Exception as e:
    #         print(e)

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
