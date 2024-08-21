from discord.ext import commands
from langdetect import detect
from deep_translator import GoogleTranslator
import discord

translate_channels= set()

def language_detector(text):
    detected = detect(text)
    return detected

def translate_to_english(text, target_language='en'):
    translated = GoogleTranslator(source='auto', target=target_language).translate(text)
    return translated

@commands.command(name="ttt", help="!ttt <text>")
async def translate(ctx, *, message: str):
    translated_Data = translate_to_english(message)
    embed = discord.Embed(
        title="Translation",
        description=translated_Data,
        color=discord.Color.green()  
    )
    await ctx.send(embed= embed)

@commands.command(name="translate")
async def start_translate(ctx):
    global translate_channels
    if(ctx.channel.id in translate_channels):
        translate_channels.remove(ctx.channel.id)

        #embed object
        embed = discord.Embed(
        title="Translation session stopped !!",
        color=discord.Color.red()  
        )
        await ctx.send(embed= embed)
    else:
        translate_channels.add(ctx.channel.id)
        embed = discord.Embed(
        title="Translation session started !!",
        color=discord.Color.green()  
        )
        await ctx.send(embed= embed)


#handler
async def on_message_translate(message, bot):
    global translate_channels

    if message.channel.id in translate_channels:
        if message.author.bot:
            return
        
        if message.content.startswith('!'):        
            return

        
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
            
        except Exception as e:
            print(f"Error detecting language: {e}")

        await bot.process_commands(message)
