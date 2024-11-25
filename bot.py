import os
import discord
import asyncio
from discord.ext import commands
from special.chat import *
from special.translate import *
from system.groups import create_group, role_group, channel_group, raffle_group


intents = discord.Intents.default()
intents.guilds = True
intents.members = True  
intents.presences = True  


bot = commands.Bot(command_prefix='!', intents=intents) #Incase need to add default commands

# App_commands (Slash commands)
async def load_all_cogs():
    # List of all cogs to load
    cogs = [
        "basics.channel",
        "basics.create_events",
        "basics.create_posts",
        "basics.create_polls",
        "basics.create_announcements",
        "basics.embeds",
        "basics.reminder",
        "basics.reaction_roles",
        "basics.roles",
        'basics.system',
        "basics.levelling_system",
        "basics.tickets",
        "basics.welcome",
        "Moderation.auto_mod_init",
        "Moderation.profanity_check",
        "Moderation.spam_detect",
        "Moderation.caps_lock",
        "Moderation.links_and_invites",
        "Moderation.temp_ban",
        "Moderation.permanent_ban",
        "Moderation.manual.blacklist",
        "Moderation.manual.create_channels",
        "Moderation.manual.mute",
        "Moderation.manual.kick",
        "Moderation.manual.custom_ban",
        "Moderation.manual.slowmode",
        "Moderation.manual.invites_tracker",
        "Moderation.manual.whitelist_links",
        "games.raffle",
        "games.quiz",
        "games.hangman",
        "games.tictactoe",
        "special.image_filter",
        "special.verification",
        "special.translate",
        "special.chat",
        "special.music_player",
    ]

    tasks = [bot.load_extension(cog) for cog in cogs]
    await asyncio.gather(*tasks)



@bot.event
async def on_ready():
    #Register groups
    bot.tree.add_command(create_group)
    bot.tree.add_command(role_group)
    bot.tree.add_command(channel_group) 
    bot.tree.add_command(raffle_group) 
        
    await load_all_cogs()
    print(f'Logged in as {bot.user}')
    await bot.tree.sync()

 
bot.run(os.getenv('DISCORD_TOKEN'))
