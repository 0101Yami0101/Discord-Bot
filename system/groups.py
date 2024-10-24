import discord

create_group= discord.app_commands.Group(name="create", description="Create anything (Channels, roles, announcements, embeds, reminders, etc).")
role_group = discord.app_commands.Group(name="role", description="Role management commands.")
channel_group = discord.app_commands.Group(name="channel", description="Channel management commands.")
