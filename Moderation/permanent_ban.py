import discord
from discord.ext import commands
from datetime import timedelta
from Moderation import auto_mod_init
from Moderation.auto_mod_init import userViolationCount

class PermanentBanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
 
        if "permban" not in auto_mod_init.moderationSession:
            return
        
        if message.author.bot: 
            return
        
        user_id = message.author.id
        
        if userViolationCount.get(user_id, 0) < 8:
            return
  
        if userViolationCount.get(user_id, 0) == 8:
            
            await self.permanently_ban_user(message.guild, message.author)
            userViolationCount.pop(user_id)

    async def permanently_ban_user(self, guild: discord.Guild, user: discord.Member):

        try:
            await user.send(f"You have been permanently banned from {guild.name} for repeated violations.")
            await guild.ban(user, reason="Exceeded violation count", delete_message_days=1)
            userViolationCount.pop(user.id)
            
        except discord.Forbidden:
            print(f"Permission error: Unable to ban {user.name} in {guild.name}")
        except Exception as e:
            print(f"An error occurred while trying to ban {user.name}: {e}")


async def setup(bot):
    await bot.add_cog(PermanentBanCog(bot))
