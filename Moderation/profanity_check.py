from better_profanity import profanity
import discord
from discord.ext import commands
from Moderation import auto_mod_init
from Moderation.auto_mod_init import userViolationCount  # Import the userViolationCount dict

class ProfanityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        
        if message.author.bot:
            return

        if "profanity" in auto_mod_init.moderationSession:

            if profanity.contains_profanity(message.content):
                try:

                    await message.delete()
                except:
                    print("Unable to delete message")
                
                #Increment violation count
                user_id = message.author.id
                if user_id in userViolationCount:
                    userViolationCount[user_id] += 1
                else:
                    userViolationCount[user_id] = 1
                    
                warning_message = f"⚠️ {message.author.mention}, your message contains inappropriate language. Please refrain from using profanity. This is a warning, further violations may result in action."
                await message.channel.send(warning_message, delete_after=6)

# Add the Cog to the bot
async def setup(bot):
    await bot.add_cog(ProfanityCog(bot))
