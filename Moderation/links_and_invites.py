import discord
import re
from discord.ext import commands
from Moderation import auto_mod_init
from Moderation.auto_mod_init import userViolationCount
from Moderation.manual.whitelist_links import white_listed_urls

# Regex patterns for detecting URLs and Discord invite links
URL_REGEX = r'(https?://[^\s]+)'
DISCORD_INVITE_REGEX = r'(discord\.gg|discordapp\.com/invite)'

class LinkAndInviteFilterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if "linkfilter" not in auto_mod_init.moderationSession:
            return
        if message.author.bot: 
            return

        if self.is_author_admin_or_higher(message):
            return

        if self.contains_link_or_invite(message.content):
    
            urls = re.findall(URL_REGEX, message.content)
            
            if any(self.is_whitelisted(url) for url in urls):
                return  
            await message.channel.send(f"🚫 {message.author.mention}, sharing links or invites is not allowed.", delete_after=6)
            await message.delete()

            # Increment user violation count
            user_id = message.author.id
            if user_id in userViolationCount:
                userViolationCount[user_id] += 1
            else:
                userViolationCount[user_id] = 1

        await self.bot.process_commands(message)

    def contains_link_or_invite(self, message_content: str):
        """Detect if a message contains a link or a Discord invite."""
        return re.search(URL_REGEX, message_content) or re.search(DISCORD_INVITE_REGEX, message_content)

    def is_whitelisted(self, url: str):
        """Check if the URL is in the whitelist or matches a whitelisted URL."""
        for whitelisted in white_listed_urls:

            if url == whitelisted:
                return True
            elif whitelisted in url:
                return True
            elif url in whitelisted:
                return True
        return False

    def is_author_admin_or_higher(self, message: discord.Message):
        """Check if the message author is an admin or has a higher role than the bot."""
     
        if message.author.guild_permissions.administrator:
            return True

        bot_member = message.guild.me  
        if message.author.top_role > bot_member.top_role:
            return True

        return False

# Add Cog to the bot
async def setup(bot):
    await bot.add_cog(LinkAndInviteFilterCog(bot))
