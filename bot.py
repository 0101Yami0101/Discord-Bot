import os
import discord
from discord.ext import commands
from Moderation.manual import whitelist_links
from special.chat import *
from special.translate import *
from basics import reminder, system, welcome_goodbye, create_polls, tickets, embeds, reaction_roles


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
app_commands= [
    system.info,
    system.avatar,
    reminder.set_reminder,
    reaction_roles.reaction,
    whitelist_links.whitelist_url,
    # levelling_system.toggle_leveling
]

async def register_app_commands():
    # Register commands from the app_commands list
    for command in app_commands:   
        bot.tree.add_command(command)
    
    # # Register commands from loaded cogs
    # for cog in bot.cogs.values():
    #     for command in cog.tree_commands:
    #         bot.tree.add_command(command)
    
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
    # Load all necessary cogs here
    await bot.load_extension("basics.reaction_roles")
    await bot.load_extension("basics.levelling_system")
    await bot.load_extension("Moderation.auto_mod_init")
    await bot.load_extension("Moderation.profanity_check")
    await bot.load_extension("Moderation.spam_detect")
    await bot.load_extension("Moderation.caps_lock")
    await bot.load_extension("Moderation.links_and_invites")
    await bot.load_extension("Moderation.temp_ban")
    await bot.load_extension("Moderation.permanent_ban")
    await bot.load_extension("Moderation.manual.blacklist")
    await bot.load_extension("Moderation.manual.mute")
    await bot.load_extension("Moderation.manual.kick")
    await bot.load_extension("Moderation.manual.custom_ban")
    await bot.load_extension("Moderation.manual.slowmode")
    await bot.load_extension("special.image_filter")
    await bot.load_extension("special.verification")



# System commands
@bot.event
async def on_ready():
    await load_all_cogs()
    print(f'Logged in as {bot.user}')
    #Register app commands
    await register_app_commands()
    #Load Cogs







# run bot
bot.run(os.getenv('DISCORD_TOKEN'))
