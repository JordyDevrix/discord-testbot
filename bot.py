import datetime
import json
import platform
import random
from openai import OpenAI
import random_functions

import discord
from discord import FFmpegPCMAudio
from discord.ext import commands, tasks
from discord.ext.commands import CheckFailure

import jumboreq
import supabase_connector
import verkeersopgaven
from lethal_functions import OpenNewQuestion
from permission_check import *


def run_discord_bot():

    with open("supacredentials.json", "r") as file:
        data = json.load(file)
        api_key = data.get("GPT_KEY")
        client = OpenAI(api_key=api_key)

    def has_admin_role(ctx: commands.Context):
        role_list = []
        for role in ctx.author.roles:
            role_list.append(role.id)

        print(role_list)
        if supabase_connector.get_admin_role(ctx.guild.id)[0].get('admin_role') in role_list:
            return True
        else:
            return False

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

    @bot.hybrid_command(name="chat", description="Use the bot's AI functionality")
    @commands.guild_only()
    async def chat(ctx: commands.Context, msg):
        msg_edit = await ctx.reply(":arrows_clockwise: Generating response...")
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": msg}
                ]
            )
            await msg_edit.edit(content=f"`q='{msg}'`\n{response.choices[0].message.content}")
        except Exception as e:
            print(e)
            await ctx.send("Something went wrong")

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
                message += f"{idx+1} - {discord.utils.get(ctx.guild.roles, id=role)}\n"

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

    @bot.hybrid_command(name="set_admin_role", description="Set a role as moderator role")
    @commands.guild_only()
    @commands.check(has_administrator_permission)
    async def set_admin_role(ctx: commands.Context, role: discord.Role):
        try:
            server_id = ctx.guild.id
            server_name = ctx.guild.name
            role_id = role.id
            print(role_id)
            supabase_connector.set_role(server_id, server_name, role_id, "admin_role")
            await ctx.send("**Rol is toegevoegd**")
        except Exception as e:
            print(e)
            await ctx.send("**Er ging iets fout, probeer het later opnieuw**")

    @bot.hybrid_command(name="set_moderator_role", description="Set a role as moderator role")
    @commands.guild_only()
    @commands.check(has_administrator_permission)
    async def set_moderator_role(ctx: commands.Context, role: discord.Role):
        try:
            server_id = ctx.guild.id
            server_name = ctx.guild.name
            role_id = role.id
            print(role_id)
            supabase_connector.set_role(server_id, server_name, role_id, "moderator_role")
            await ctx.send("**Rol is toegevoegd**")
        except Exception as e:
            print(e)
            await ctx.send("**Er ging iets fout, probeer het later opnieuw**")

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

    @bot.hybrid_command(name="deletelog", description="Show all the deleted messages from your server")
    @commands.guild_only()
    @commands.check(has_administrator_permission)
    async def deletelog(ctx: commands.Context, amount=1):
        server_id = ctx.guild.id
        messages = supabase_connector.get_deleted_messages(server_id)
        messages_sorted = sorted(messages, key=lambda x: x['id'])
        messages_sorted.reverse()
        if len(messages) == 0:
            await ctx.send("No deleted messages found")
        else:
            if amount > 10:
                await ctx.send("Please do not request more then 10 messages")
            else:
                if amount == 1:
                    await ctx.send(f"Sending last message")
                else:
                    await ctx.send(f"Sending last {amount} messages")
                for i in range(amount):
                    msg: dict = messages_sorted[i]
                    msg_time = msg.get('message_time').split('.')[0].split('T')
                    await ctx.send(f"`ID:{msg.get('id')} | {msg_time[0]} {msg_time[1]} | {msg.get('user_name')}`\n"
                                   f"{msg.get('message')}\n"
                                   f"{msg.get('attachment')}")

    @deletelog.error
    async def deletelog_error(ctx: commands.Context, error):
        if isinstance(error, PermissionError):
            await ctx.reply("no perms, cry cry :_(", ephemeral=True)
        else:
            await ctx.send("Something went wrong try again later or contact the developer")

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
                for server in data:
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

                await ctx.send(f"Announcement made by {ctx.author.mention}")
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

    @bot.hybrid_command()
    async def ping(ctx: commands.Context):
        await ctx.send("pong")

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
                    removed = True
                if len(ctx.guild.voice_channels) == idx + 1 and not removed:
                    await ctx.send("**Je moet eerst een voicechannel joinen**")
        except Exception as e:
            print(e)
            await ctx.send("**Bot is niet aanwezig in een voice channel**")

    @bot.hybrid_command(name="playradio", description="play music")
    @commands.guild_only()
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
            # await ctx.send("**Er is niemand aanwezig in een voicechannel**")
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

    # Moderation functies #

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

    @bot.hybrid_command(name="kick", description="kick a member from the server")
    @commands.guild_only()
    @commands.check(has_kick_permission)
    async def kick(ctx: commands.Context, member: discord.Member, reason=None):
        print(f"{ctx.command} -- {member} -- {commands.bot_has_permissions()}")
        if ctx.author.id == member.id:
            await ctx.send("You cannot kick yourself")
        else:
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

    @bot.event
    async def on_ready():
        print("bot running")
        change_status.start()
        await bot.tree.sync()

    # Auto disconnect discord bot from voicechannel and change RPC #

    @bot.event
    async def on_message_delete(message: discord.Message):
        attachmentlist = ""
        for idx, attachment in enumerate(message.attachments):
            attachmentlist += f"{attachment.url}\n"

        deleter = ""
        async for entry in message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
            deleter = entry.user

        try:
            if supabase_connector.get_deletelog_permission(message.guild.id)[0].get('deletelog'):
                supabase_connector.add_new_chatlog(
                    message.guild.name,
                    message.guild.id,
                    message.author.id,
                    message.author.name,
                    message.content,
                    message.channel.name,
                    attachmentlist,
                    deleter.id
                )
        except Exception as e:
            print(e)

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
