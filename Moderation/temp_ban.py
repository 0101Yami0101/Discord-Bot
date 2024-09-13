import discord
from discord.ext import commands
from datetime import timedelta
from Moderation import auto_mod_init
from Moderation.auto_mod_init import userViolationCount, moderationSession

class TempBanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if "tempban" not in auto_mod_init.moderationSession:
            return
        
        if message.author.bot:  # Ignore messages from bots
            return

        user_id = message.author.id
  

        # Check if the user has hit the violation threshold
        if userViolationCount.get(user_id, 0) >= 4:
            
            await self.temp_ban_user(message.guild, message.author)
            userViolationCount[user_id] = 0  # Reset the violation count after the ban

    async def temp_ban_user(self, guild: discord.Guild, user: discord.Member):
        """Ban the user temporarily for 1 day (24 hours)."""
        try:
            await guild.ban(user, reason="Exceeded violation count", delete_message_days=1)
            await user.send(f"You have been banned from {guild.name} for 24 hours due to repeated violations.")

            # Schedule unban after 24 hours
            await discord.utils.sleep_until(discord.utils.utcnow() + timedelta(days=1))
            await guild.unban(user)

            await user.send(f"You have been unbanned from {guild.name} after serving a 24-hour temporary ban.")
        except discord.Forbidden:
            print(f"Permission error: Unable to ban {user.name} in {guild.name}")
        except Exception as e:
            print(f"An error occurred while trying to ban {user.name}: {e}")

# Add Cog to the bot
async def setup(bot):
    await bot.add_cog(TempBanCog(bot))
