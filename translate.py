from discord.ext import commands
from langdetect import detect
from deep_translator import GoogleTranslator
import discord

translationSession= False

def language_detector(text):
    detected = detect(text)
    return detected

def translate_to_english(text, target_language='en'):
    translated = GoogleTranslator(source='auto', target=target_language).translate(text)
    return translated

@commands.command(name="tt")
async def translate(ctx, *, message: str):
    translated_Data = translate_to_english(message)
    await ctx.send(translated_Data)

@commands.command(name="starttr")
async def start_translate(ctx):
    global translationSession
    if(translationSession):
        translationSession= False

        #embed object
        embed = discord.Embed(
        title="Translation session stopped !!",
        color=discord.Color.red()  
        )
        await ctx.send(embed= embed)
    else:
        translationSession= True
        embed = discord.Embed(
        title="Translation session started !!",
        color=discord.Color.green()  
        )
        await ctx.send(embed= embed)


#handler
async def on_message_translate(message, bot):
    global translationSession

    if translationSession:
        if message.author.bot:
            return
        
        if message.content.startswith('!'):        
            return

        if message.channel.id == 1113450097808773241:  #Only readInfo channel for now
            try:
                detected_lang = language_detector(message.content)
                if detected_lang != 'en':
                    translated_Data = translate_to_english(message.content)
                    embed = discord.Embed(
                        title="Translation",
                        description=translated_Data,
                        color=discord.Color.yellow()  
                        )
                    await message.channel.send(embed=embed)
                else:
                    print("English")
            except Exception as e:
                print(f"Error detecting language: {e}")

        await bot.process_commands(message)
