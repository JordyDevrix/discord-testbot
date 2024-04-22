from discord.ext import commands


def has_administrator_permission(ctx: commands.Context):
    return ctx.author.guild_permissions.administrator


def has_kick_permission(ctx: commands.Context):
    return ctx.author.guild_permissions.kick_members


def has_timeout_permission(ctx: commands.Context):
    return ctx.author.guild_permissions.mute_members


def has_untimeout_permission(ctx: commands.Context):
    return ctx.author.guild_permissions.mute_members


def has_ban_permission(ctx: commands.Context):
    return ctx.author.guild_permissions.ban_members


def has_manage_server_permission(ctx: commands.Context):
    return ctx.author.guild_permissions.manage_guild


def has_manage_permissions_permission(ctx: commands.Context):
    return ctx.author.guild_permissions.manage_permissions


def has_manage_roles_permission(ctx: commands.Context):
    return ctx.author.guild_permissions.manage_roles


def has_manage_messages_permission(ctx: commands.Context):
    return ctx.author.guild_permissions.manage_messages


def has_mention_everyone_permission(ctx: commands.Context):
    return ctx.author.guild_permissions.mention_everyone


def has_manage_channels_permission(ctx: commands.Context):
    return ctx.author.guild_permissions.manage_channels
