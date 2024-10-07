import os
import discord
import asyncio
from discord.ext import commands
from Moderation.manual import whitelist_links
from special.chat import *
from special.translate import *
from basics import reminder, system, welcome_goodbye, create_polls, tickets, embeds, reaction_roles
from system.groups import create_group

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
bot = commands.Bot(command_prefix='!', intents=intents)


#Add Custom commands (names)
#Default type ( ! )
commands = [
    translate,
    start_translate,
    start_chat_bot,
    create_polls.poll,
    tickets.create_ticket_channel,
    embeds.create_embed,
    
]
for command in commands:
    bot.add_command(command)



# App_commands (Slash commands)
app_commands_list= [
    system.info,
    system.avatar,
    reminder.set_reminder,
    reaction_roles.reaction,
    whitelist_links.whitelist_url,
    # levelling_system.toggle_leveling
]

async def register_app_commands():
    for command in app_commands_list:   
        bot.tree.add_command(command)
    
    
    await bot.tree.sync()

# Wrappers
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
bot.add_listener(chatbot_wrapper, 'on_message')
bot.add_listener(on_message_wrapper, 'on_message')
bot.add_listener(welcomeWrapper, 'on_member_join')
bot.add_listener(goodbyeWrapper, 'on_member_remove')
bot.add_listener(ticketOpenWrapper, 'on_interaction')
bot.add_listener(createEmbedWrapper, 'on_interaction')
bot.add_listener(onAttachmentUploadWrapper, 'on_message')


async def load_all_cogs():
    # List of all cogs to load
    cogs = [
        "basics.create_announcements",
        "basics.create_posts",
        "basics.reaction_roles",
        "basics.levelling_system",
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
        "special.image_filter",
        "special.verification"
    ]

    # Create a list of tasks to load each cog
    tasks = [bot.load_extension(cog) for cog in cogs]

    # Run all tasks concurrently
    await asyncio.gather(*tasks)



# System commands
@bot.event
async def on_ready():
    #Register groups
    bot.tree.add_command(create_group) #CREATE CLASS FOR GROUPS

    await load_all_cogs()
    print(f'Logged in as {bot.user}')
   
    await register_app_commands()
    await bot.tree.sync()








# run bot
bot.run(os.getenv('DISCORD_TOKEN'))
