from discord.ext import commands
import discord
import asyncio

@commands.command(name='poll')
async def poll(ctx):
    await ctx.send("Please enter the poll question:")
    
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    
    try:
        #poll question
        question_msg = await ctx.bot.wait_for('message', timeout=60.0, check=check)
        question = question_msg.content
        
        await ctx.send("Now enter the poll options separated by commas (e.g., option1, option2, option3):")
        
        #poll options
        options_msg = await ctx.bot.wait_for('message', timeout=60.0, check=check)
        options = options_msg.content.split(',')
        options = [option.strip() for option in options if option.strip()]
        
        if len(options) < 2:
            await ctx.send("You need at least two options to create a poll.")
            return

        if len(options) > 9:
            await ctx.send("You can only have up to 9 options for the poll.")
            return
        

        embed = discord.Embed(title=question, description='\n'.join([f"{chr(97+i)}: {option}" for i, option in enumerate(options)]), color=discord.Color.blue())

        poll_message = await ctx.send(embed=embed)
        
        emoji_list = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮']

        for i in range(len(options)):
            emoji = emoji_list[i]  # Use Unicode emojis
            await poll_message.add_reaction(emoji)
        

        await ctx.send("React with the corresponding emojis to vote.")
    
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond. Please try again.")
    except discord.HTTPException as e:
        await ctx.send(f"An error occurred: {e}")