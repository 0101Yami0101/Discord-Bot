from discord.ext import commands
from discord import app_commands
from langdetect import detect
from deep_translator import GoogleTranslator
import discord

class TranslateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translate_channels = set()  # Tracks channels where translation is active

    def language_detector(self, text):
        """Detects the language of the given text."""
        return detect(text)

    def translate_to_english(self, text, target_language='en'):
        """Translates the given text to the target language."""
        return GoogleTranslator(source='auto', target=target_language).translate(text)

    # App command group for translation
    translate_commands_group = app_commands.Group(name="translate", description="Manage translation in channels.")

    @translate_commands_group.command(name="start", description="Start translating messages in this channel.")
    async def start_translate(self, interaction: discord.Interaction):
        """Start translating messages in the current channel."""
        if interaction.channel_id in self.translate_channels:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Translation is already active in this channel!",
                    color=discord.Color.yellow()
                ),
                ephemeral=True
            )
        else:
            self.translate_channels.add(interaction.channel_id)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Translation session started!",
                    color=discord.Color.green()
                ),
                ephemeral=True
            )

    @translate_commands_group.command(name="stop", description="Stop translating messages in this channel.")
    async def stop_translate(self, interaction: discord.Interaction):
        """Stop translating messages in the current channel."""
        if interaction.channel_id in self.translate_channels:
            self.translate_channels.remove(interaction.channel_id)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Translation session stopped!",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Translation is not active in this channel.",
                    color=discord.Color.yellow()
                ),
                ephemeral=True
            )

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handles automatic translation of messages."""
        if (
            message.author.bot  # Ignore bot messages
            or message.channel.id not in self.translate_channels  # Ignore non-translate channels
        ):
            return

        try:
            detected_lang = self.language_detector(message.content)
            if detected_lang != 'en':
                translated_data = self.translate_to_english(message.content)
                await message.channel.send(embed=discord.Embed(
                    title="Translation",
                    description=translated_data,
                    color=discord.Color.blue()
                ))
        except Exception as e:
            print(f"Error detecting or translating message: {e}")

# Setup function for the cog
async def setup(bot: commands.Bot):
    await bot.add_cog(TranslateCog(bot))

