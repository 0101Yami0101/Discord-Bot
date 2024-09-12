import discord
import time
from collections import defaultdict
from discord.ext import commands
from Moderation import auto_mod_init


user_message_timestamps = defaultdict(list)
MAX_MESSAGES = 4 
TIME_FRAME = 8

def is_spam(user_id):
    """Check if the user is spamming based on message timestamps."""
    now = time.time()
    timestamps = user_message_timestamps[user_id]
    
    user_message_timestamps[user_id] = [t for t in timestamps if now - t <= TIME_FRAME]
    
    if len(user_message_timestamps[user_id]) >= MAX_MESSAGES:
        return True
    return False


class SpamDetectCog(commands.Cog):
    def __init__(self, bot):
        self.bot= bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if "spam" not in auto_mod_init.moderationSession :
            return
        if message.author.bot:
            return
         
        user_id = message.author.id
        now = time.time()
        
        # Track the message timestamp for the user
        user_message_timestamps[user_id].append(now)

        if is_spam(user_id):
            await message.channel.send(f"⚠️ {message.author.mention}, you're sending messages too fast! Please slow down.", delete_after=6)
            await message.delete()  
        await self.bot.process_commands(message)


#add Cog to the bot
async def setup(bot):
    await bot.add_cog(SpamDetectCog(bot))
