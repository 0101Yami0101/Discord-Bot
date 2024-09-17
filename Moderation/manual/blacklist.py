import discord
from discord.ext import commands
from discord import app_commands
from Moderation.auto_mod_init import userViolationCount

class BlackListCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blacklisted_words_phrases = []

    # Create a command group for the blacklist commands
    blacklist_group = app_commands.Group(name="blacklist", description="Blacklist words or phrases.")

    @blacklist_group.command(name='add', description='Add words or phrases to blacklist')
    @app_commands.checks.has_permissions(administrator=True)
    async def add_to_blacklist(self, interaction: discord.Interaction, word_or_phrase: str):
        # Add the word or phrase to the blacklist
        self.blacklisted_words_phrases.append(word_or_phrase.lower())
        await interaction.response.send_message(f"Added `{word_or_phrase}` to the blacklist.", ephemeral=True)
    
    @blacklist_group.command(name='remove', description='Remove words or phrases from blacklist')
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_from_blacklist(self, interaction: discord.Interaction, word_or_phrase: str):
        # Remove the word or phrase from the blacklist if it exists
        if word_or_phrase.lower() in self.blacklisted_words_phrases:
            self.blacklisted_words_phrases.remove(word_or_phrase.lower())
            await interaction.response.send_message(f"Removed `{word_or_phrase}` from the blacklist.", ephemeral=True)
        else:
            await interaction.response.send_message(f"`{word_or_phrase}` is not in the blacklist.", ephemeral=True)
    
    @blacklist_group.command(name='list', description='Get a list of all blacklisted words and phrases')
    @app_commands.checks.has_permissions(administrator=True)
    async def list_blacklist(self, interaction: discord.Interaction):
        # List all blacklisted words and phrases
        if self.blacklisted_words_phrases:
            blacklist_str = ', '.join(self.blacklisted_words_phrases)
            await interaction.response.send_message(f"Blacklisted words/phrases: {blacklist_str}", ephemeral=True)
        else:
            await interaction.response.send_message("The blacklist is currently empty.", ephemeral=True)
    
    @blacklist_group.command(name='clear', description='Clear blacklist')
    @app_commands.checks.has_permissions(administrator=True)
    async def clear_blacklist(self, interaction: discord.Interaction):
        # Clear all words and phrases from the blacklist
        self.blacklisted_words_phrases.clear()
        await interaction.response.send_message("Cleared all items from the blacklist.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author.bot:
            return

        if self.blacklisted_words_phrases:
            for word_or_phrase in self.blacklisted_words_phrases:
                if word_or_phrase in message.content.lower():
                    try:

                        await message.delete()
                        user_id = message.author.id
                        if user_id in userViolationCount:
                            userViolationCount[user_id] += 1
                        else:
                            userViolationCount[user_id] = 1
                        await message.channel.send(f"{message.author.mention}, your message contains a blacklisted word/phrase and has been deleted.")
                    except discord.Forbidden:
                        
                        await message.channel.send("I don't have permission to delete messages here.")
                    break 

async def setup(bot: commands.Bot):
    await bot.add_cog(BlackListCog(bot))
