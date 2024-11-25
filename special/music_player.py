import discord
from discord.ext import commands
from discord import app_commands, Interaction
import yt_dlp
import asyncio
import re, os

class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}

    music_group = app_commands.Group(
        name="music",
        description="Music control commands."
    )

    @music_group.command(name='join', description='Join the voice channel you are in')
    async def join(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        if interaction.user.voice is None:
            embed = discord.Embed(
                title="Error",
                description="You are not connected to a voice channel.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return

        channel = interaction.user.voice.channel

        if interaction.guild.voice_client is not None:
            await interaction.guild.voice_client.move_to(channel)
        else:
            await channel.connect()

        embed = discord.Embed(
            title="Joined",
            description=f"Joined {channel.name}",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed)

    @music_group.command(name='play', description='Play a song in the voice channel')
    async def play(self, interaction: Interaction, query: str):
        await interaction.response.defer()

        voice_client = interaction.guild.voice_client
        if voice_client is None:
            embed = discord.Embed(
                title="Error",
                description="I am not connected to a voice channel. Use /join first.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        if interaction.guild.id not in self.queue:
            self.queue[interaction.guild.id] = []

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if re.match(r'https?://', query):
                    info = ydl.extract_info(query, download=False)
                else:
                    search_query = f"ytsearch1:{query}"
                    info = ydl.extract_info(search_query, download=False)['entries'][0]
                
                audio_url = info['url']
                title = info.get('title', 'Unknown')
                webpage_url = info.get('webpage_url', '')

                self.queue[interaction.guild.id].append((audio_url, title, webpage_url))
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to fetch audio: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title="Added to Queue",
            description=f"[{title}]({webpage_url})",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed)

        if not voice_client.is_playing():
            await self.play_next(interaction.guild.id)

    async def play_next(self, guild_id):
        voice_client = self.bot.get_guild(guild_id).voice_client

        if not self.queue[guild_id]:
            if not voice_client.is_playing():
                await asyncio.sleep(5)
                await voice_client.disconnect()
                del self.queue[guild_id]
            return

        audio_url, title, webpage_url = self.queue[guild_id].pop(0)
        ffmpeg_path = os.getenv('FFMPEG_PATH')
        ffmpeg_options = {
            'options': '-vn',
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        }
        audio_source = discord.FFmpegPCMAudio(audio_url, executable=ffmpeg_path, **ffmpeg_options)

        def after_play(error):
            if error:
                print(f"Error during playback: {error}")
            coro = self.play_next(guild_id)
            asyncio.run_coroutine_threadsafe(coro, self.bot.loop)

        voice_client.play(audio_source, after=after_play)

        embed = discord.Embed(
            title="Now Playing",
            description=f"[{title}]({webpage_url})",
            color=discord.Color.green()
        )
        channel = self.bot.get_guild(guild_id).text_channels[0]
        asyncio.run_coroutine_threadsafe(channel.send(embed=embed), self.bot.loop)

    @music_group.command(name='skip', description='Skip the current song')
    async def skip(self, interaction: Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            embed = discord.Embed(
                title="Skipped",
                description="Skipped the current song.",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Error",
                description="No song is currently playing.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @music_group.command(name='queue', description='Show the current song queue')
    async def show_queue(self, interaction: Interaction):
        if interaction.guild.id not in self.queue or not self.queue[interaction.guild.id]:
            embed = discord.Embed(
                title="Queue",
                description="The queue is empty.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        queue_list = "\n".join([f"{idx + 1}. [{title}]({url})" for idx, (url, title, webpage_url) in enumerate(self.queue[interaction.guild.id])])
        embed = discord.Embed(
            title="Current Queue",
            description=queue_list,
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @music_group.command(name='leave', description='Disconnect from the voice channel')
    async def leave(self, interaction: Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client:
            await voice_client.disconnect()
            del self.queue[interaction.guild.id]
            embed = discord.Embed(
                title="Disconnected",
                description="Disconnected from the voice channel.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Error",
                description="I am not connected to any voice channel.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))