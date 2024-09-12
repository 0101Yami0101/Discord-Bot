import discord
import re
from discord.ext import commands
from Moderation import auto_mod_init

# Regex patterns for detecting URLs and Discord invite links
URL_REGEX = r'(https?://[^\s]+)'
DISCORD_INVITE_REGEX = r'(discord\.gg|discordapp\.com/invite)'

class LinkAndInviteFilterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if "linkfilter" not in auto_mod_init.moderationSession:  # Ensure the link filter is enabled
            return
        if message.author.bot:  # Ignore messages from bots
            return

        if self.contains_link_or_invite(message.content):
            await message.channel.send(f"🚫 {message.author.mention}, sharing links or invites is not allowed.", delete_after=6)
            await message.delete()

        await self.bot.process_commands(message)

    def contains_link_or_invite(self, message_content: str):
        """Detect if a message contains a link or a Discord invite."""
        return re.search(URL_REGEX, message_content) or re.search(DISCORD_INVITE_REGEX, message_content)

# Add Cog to the bot
async def setup(bot):
    await bot.add_cog(LinkAndInviteFilterCog(bot))
