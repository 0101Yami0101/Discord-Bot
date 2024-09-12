from better_profanity import profanity
import discord
from discord.ext import commands
from Moderation import auto_mod_init


class ProfanityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if "profanity" in auto_mod_init.moderationSession:

            if profanity.contains_profanity(message.content):
                await message.delete()
                embed = discord.Embed(
                    title="Warning!! ",
                    description=f"Profanity Detected in a message sent by @{message.author.name}",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed)

#add Cog to the bot
async def setup(bot):
    await bot.add_cog(ProfanityCog(bot))
