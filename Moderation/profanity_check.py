from better_profanity import profanity
import discord


async def profanity_checker (message):
    if(profanity.contains_profanity(message.content)):
        await message.delete()
        embed= discord.Embed(
            title= "Warning!! ",
            description=f"Profanity Detected in a message sent by @{message.author.name}",
            color= discord.Color.red()
        )
        await message.channel.send(embed= embed)
    



