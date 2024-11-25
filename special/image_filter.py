import discord
from discord.ext import commands
from discord import app_commands

class VoiceCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='join')
    async def join(self, ctx):
        # Check if the user is in a voice channel
        if ctx.author.voice:
            # Get the voice channel the user is in
            channel = ctx.author.voice.channel
            # Connect to the voice channel
            await channel.connect()
            await ctx.send(f'Joined {channel.name}!')
        else:
            await ctx.send('You need to join a voice channel first.')

async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceCommandsCog(bot))
