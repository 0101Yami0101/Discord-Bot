from better_profanity import profanity
import discord
from Moderation import modinit

async def profanity_checker (message):
    if(modinit.moderationSession):

        if(profanity.contains_profanity(message.content)):
            await message.delete()
            embed= discord.Embed(
                title= "Warning!! ",
                description=f"Profanity Detected in a message sent by @{message.author.name}",
                color= discord.Color.red()
            )
            await message.channel.send(embed= embed)
    



