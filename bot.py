import discord
from discord.ext import commands
import os
from chat import *
from translate import *

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)



# Custom commands
bot.add_command(translate)
bot.add_command(start_translate)
bot.add_command(start_chat_bot)

# Wrappers
async def on_message_wrapper(message):
    await on_message_translate(message, bot)

async def chatbot_wrapper(message):
    await chatbot(message, bot)


# Events and Handlers
bot.add_listener(chatbot_wrapper, 'on_message')
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
