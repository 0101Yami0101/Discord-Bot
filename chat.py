import discord, os
from discord.ext import commands
import cohere

cohere_api_key = os.getenv("COHERE_KEY")
co = cohere.Client(cohere_api_key)

chat_channels= set()

@commands.command(name="ai")
async def start_chat_bot(ctx):
    global chat_channels
    if(ctx.channel.id not in chat_channels):
        chat_channels.add(ctx.channel.id)
    else:
        chat_channels.remove(ctx.channel.id)
    await ctx.send("Started in this channel")
    


async def chatbot(message, bot):
    global chat_channels

    if message.channel.id in chat_channels:
        try:
            if message.author.bot:
                return
            
            if message.content.startswith('!'):        
                return
            
            response = co.generate(
                model='command-xlarge-nightly',  
                prompt=message.content,
                max_tokens=100, 
                temperature=0.7
            )
            response_text = response.generations[0].text.strip()

            embed = discord.Embed(
                description=response_text,
                color=discord.Color.purple() 
            )
            embed.set_thumbnail(url="https://img.freepik.com/free-vector/robotic-artificial-intelligence-technology-smart-lerning-from-bigdata_1150-48136.jpg?t=st=1723949221~exp=1723952821~hmac=49bc247e56f149a5705c5cca9a13571c21a0b344b9651bb155dffe08ab3c8f39&w=996")

            await message.channel.send(embed= embed)
        
        except Exception as e:

            await message.channel.send(f"An error occurred: {e}")
