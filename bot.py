import os
import discord
from discord.interactions import Interaction
from discord.ext import commands
from Moderation import modinit, profanity_check 
from special.chat import *
from special.translate import *
from basics import system, welcome_goodbye, create_polls, tickets, embeds

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
bot = commands.Bot(command_prefix='!', intents=intents)


# Custom commands (names)
commands = [
    translate,
    start_translate,
    start_chat_bot,
    modinit.moderation,
    create_polls.poll,
    tickets.create_ticket_channel,
    embeds.create_embed,
    
]
for command in commands:
    bot.add_command(command)


# App_commands

async def register_app_commands():  
    
    bot.tree.add_command(system.info)
    bot.tree.add_command(system.avatar)

    await bot.tree.sync()


# Wrappers
async def profanity_wrapper(message):
    await profanity_check.profanity_checker(message)

async def on_message_wrapper(message):
    await on_message_translate(message, bot)

async def chatbot_wrapper(message):
    await chatbot(message, bot)

async def welcomeWrapper(member):
    await welcome_goodbye.welcome_on_join(member= member)

async def goodbyeWrapper(member):
    await welcome_goodbye.goodbye_on_remove(member= member, bot= bot)

async def ticketOpenWrapper(Interaction):
    await tickets.on_ticket_button_interaction(interaction= Interaction)

async def createEmbedWrapper(Interaction):
    await embeds.on_buttons_interaction(interaction= Interaction)

async def onAttachmentUploadWrapper(message):
    await embeds.on_attachment_upload_message(message= message)

# Add handlers to events
bot.add_listener(profanity_wrapper, 'on_message')
bot.add_listener(chatbot_wrapper, 'on_message')
bot.add_listener(on_message_wrapper, 'on_message')
bot.add_listener(welcomeWrapper, 'on_member_join')
bot.add_listener(goodbyeWrapper, 'on_member_remove')
bot.add_listener(ticketOpenWrapper, 'on_interaction')
bot.add_listener(createEmbedWrapper, 'on_interaction')
bot.add_listener(onAttachmentUploadWrapper, 'on_message')

# System commands
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    #Register app commands
    await register_app_commands()






# run bot
bot.run(os.getenv('DISCORD_TOKEN'))
