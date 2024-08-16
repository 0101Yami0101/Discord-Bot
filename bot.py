import discord
from discord.ext import commands
import os
from chat import chatbot
from translate import *

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)



# Custom commands
bot.add_command(chatbot)
bot.add_command(translate)

# Wrappers
async def on_message_wrapper(message):
    await on_message(message, bot)

# Events and Handlers
bot.add_listener(on_message_wrapper, 'on_message')

# System commands
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def info(ctx):
    server = ctx.guild  
    member = ctx.author
    info_message = (
        f"Server name: {server.name}\n"
        f"Server ID: {server.id}\n"
        f"Your name: {member.name}\n"
        f"Your ID: {member.id}\n"
        f"Total members: {server.member_count}"
    )
    await ctx.send(info_message)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(member.avatar.url)



bot.run(os.getenv('DISCORD_TOKEN'))
