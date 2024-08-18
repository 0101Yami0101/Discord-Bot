import discord, os
from discord.ext import commands
import cohere

cohere_api_key = os.getenv("COHERE_KEY")
co = cohere.Client(cohere_api_key)
chatbotSession= False
current_channel= None

@commands.command(name="startai")
async def start_chat_bot(ctx):
    global chatbotSession
    global current_channel
    if chatbotSession and  ctx.channel.id is not current_channel:
        
        embed = discord.Embed(
                title=f"Session already running at <#{current_channel}>" ,
                color=discord.Color.from_rgb(20, 20, 20)
        )
        await ctx.send(embed= embed)
        return 
    
    elif chatbotSession and current_channel == ctx.channel.id :  
        chatbotSession= False
        current_channel= None
        embed = discord.Embed(
                title="AI Bot session stopped!!",
                color=discord.Color.from_rgb(0, 0, 0)
        )
        await ctx.send(embed= embed)
        return
        
    

    chatbotSession= True
    current_channel= ctx.channel.id
    print(current_channel)
    embed = discord.Embed(
                title="AI Bot session is running..",
                color=discord.Color.from_rgb(255, 255, 255)
        )
    await ctx.send(embed= embed)
    


async def chatbot(message, bot):
    global chatbotSession
    global current_channel
    print(current_channel)
    if chatbotSession and message.channel.id == current_channel:
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
