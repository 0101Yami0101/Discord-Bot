import discord
import time
from collections import defaultdict
from discord.ext import commands
from Moderation import auto_mod_init
from Moderation.auto_mod_init import userViolationCount

class CapsLockDetectCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if "capslock" not in auto_mod_init.moderationSession:
            return
        if message.author.bot: 
            return
        
        if self.is_excessive_caps(message.content):
            await message.channel.send(f"⚠️ {message.author.mention}, please avoid using excessive caps lock.", delete_after=6)
            await message.delete()
            user_id = message.author.id
            #Increment violation count
            if user_id in userViolationCount:
                userViolationCount[user_id] += 1
            else:
                userViolationCount[user_id] = 1

        await self.bot.process_commands(message)

    def is_excessive_caps(self, message_content: str):
        """Detect excessive use of caps lock in a message."""
        if len(message_content) < 25:  # Ignore very short messages
            return False

        caps_count = sum(1 for char in message_content if char.isupper())
        caps_ratio = caps_count / len(message_content)

        return caps_ratio > 0.7

# Add Cog to the bot
async def setup(bot):
    await bot.add_cog(CapsLockDetectCog(bot))
