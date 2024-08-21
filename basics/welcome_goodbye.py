import discord
from discord.ext import commands



#welcome handler
async def welcome_on_join(member):
    try:

        dm_path = await member.create_dm()
        embed = discord.Embed(
            title="🎉 Welcome to the Server! 🎉",
            description=f"Hello {member.mention},\n\nWe're thrilled to have you join our community! 😃\n\nHere are a few things to get you started:",
            color=discord.Color.blue()
        )
        embed.add_field(name="🌟 Introduce Yourself", value="Feel free to introduce yourself in the #introductions channel!", inline=False)
        embed.add_field(name="📜 Rules", value="Please read the rules in #rules to make sure you're up-to-date.", inline=False)
        embed.set_thumbnail(url="https://rukminim2.flixcart.com/image/850/1000/l0sgyvk0/wall-decoration/d/p/t/tree-theme-welcome-acrylic-3d-board-design-for-door-wall-hanging-original-imagcg6bmqnjnjb5.jpeg?q=90&crop=false")  
        embed.set_footer(text="Enjoy your time with us! 🌟")
        await dm_path.send(embed= embed)
    except discord.DiscordException as e:
        print(f"Failed to send DM to {member.name}: {e}")




async def goodbye_on_remove(member, bot):
    try:
       
        channel = bot.get_channel(1111744485714579476)  

        embed = discord.Embed(
            title="f{member.name} has left the server!👋",
            color=discord.Color.red()
        )

        # Send the farewell message to the general chat
        await channel.send(embed=embed)

    except discord.DiscordException as e:
        print(f"Failed to send message to the channel: {e}")