import discord
from discord.ext import commands
from discord import app_commands
import cohere
import os

cohere_api_key = os.getenv("COHERE_KEY")
co = cohere.Client(cohere_api_key)

class AIChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chat_channels = set()  

  
    ai_commands_group = app_commands.Group(name="ai", description="Manage the AI chatbot in channels.")

    @ai_commands_group.command(name="start", description="Start AI chatbot in the current channel.")
    async def start_chatbot(self, interaction: discord.Interaction):
        """Start AI chatbot in the current channel."""
        if interaction.channel_id in self.chat_channels:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="AI Chatbot is already active in this channel!",
                    color=discord.Color.yellow()
                ),
                ephemeral=True
            )
        else:
            self.chat_channels.add(interaction.channel_id)
            embed = discord.Embed(
                title="AI Chatbot Started",
                color=discord.Color.green()
            )
            embed.set_image(url="https://img.freepik.com/free-vector/robotic-artificial-intelligence-technology-smart-lerning-from-bigdata_1150-48136.jpg?t=st=1723949221~exp=1723952821~hmac=49bc247e56f149a5705c5cca9a13571c21a0b344b9651bb155dffe08ab3c8f39&w=996")
            await interaction.response.send_message(embed=embed, ephemeral=False)

    @ai_commands_group.command(name="stop", description="Stop AI chatbot in the current channel.")
    async def stop_chatbot(self, interaction: discord.Interaction):
        """Stop AI chatbot in the current channel."""
        if interaction.channel_id in self.chat_channels:
            self.chat_channels.remove(interaction.channel_id)
            embed = discord.Embed(
                title="AI Chatbot Stopped",
                color=discord.Color.dark_grey()
            )
            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="AI Chatbot is not active in this channel.",
                    color=discord.Color.yellow()
                ),
                ephemeral=True
            )

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handles AI chatbot interactions."""
        if (
            message.author.bot  # Ignore bot messages
            or message.channel.id not in self.chat_channels  # Ignore non-chatbot channels
        ):
            return

        try:

            temPembed = discord.Embed(
                description="Generating response...",
                color=discord.Color.green()
            )
            loading_message = await message.channel.send(embed=temPembed)

            response = co.generate(
                model="command-xlarge-nightly",
                prompt=message.content,
                max_tokens=100,
                temperature=0.7
            )
            response_text = response.generations[0].text.strip()

     
            embed = discord.Embed(
                description=response_text,
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url="https://img.freepik.com/free-vector/robotic-artificial-intelligence-technology-smart-lerning-from-bigdata_1150-48136.jpg?t=st=1723949221~exp=1723952821~hmac=49bc247e56f149a5705c5cca9a13571c21a0b344b9651bb155dffe08ab3c8f39&w=996")
            await loading_message.edit(embed=embed)

        except Exception as e:
            await message.channel.send(f"An error occurred: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(AIChatCog(bot))
