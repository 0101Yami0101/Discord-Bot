import discord
from discord.ext import commands
from functions import *
import os

# Create an instance of the Client class
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Event when the bot has connected to the server
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

@bot.command()
async def ping(ctx):
    await ctx.send(f' Latency is {round(bot.latency * 1000)}ms')

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

@bot.command(name="tt")
async def translate(ctx, *, message: str):
    translated_Data= translate_to_english(message)
    
    await ctx.send(translated_Data)


# AutoTranslate in one channel
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id == 1113450097808773241:
        try:
            detected_lang = language_detector(message.content)
            if detected_lang != 'en':
                translated_Data= translate_to_english(message.content)
                await message.channel.send(f"translated->->->   {translated_Data}")
            else:
                print("English")
        except Exception as e:
            print(f"Error detecting language: {e}")

    await bot.process_commands(message)



bot.run(os.getenv('DISCORD_TOKEN'))
