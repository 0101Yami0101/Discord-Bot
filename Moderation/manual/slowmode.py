import discord
from discord import app_commands
from discord.ext import commands

class SlowmodeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    slowmode_commands_group = app_commands.Group(name="slowmode", description="Manage slowmode in channels.")

    @slowmode_commands_group.command(name="channel", description="Set slowmode for a specific channel (Max: 6 hours).")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(channel="Select the channel", cooldown="Cooldown duration (e.g., 5s, 10m, 1h)")
    async def set_channel_slowmode(self, interaction: discord.Interaction, channel: discord.TextChannel, cooldown: str):
        cooldown_seconds = self.parse_cooldown(cooldown)

        await interaction.response.send_message(f"Setting Slowmode in {channel.mention}. Cooldown: {cooldown}", ephemeral=True)
        if cooldown_seconds is None or cooldown_seconds > 21600:  # Max 6 hours = 21600 seconds
            await interaction.followup.send("Invalid cooldown. Please provide a valid cooldown (Max: 6 hours).", ephemeral=True)
            return

        await channel.edit(slowmode_delay=cooldown_seconds)
        await interaction.followup.send(f"Slowmode set in {channel.mention}", ephemeral=True)

    @slowmode_commands_group.command(name="all", description="Set slowmode for all channels (Max: 6 hours).")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(cooldown="Cooldown duration (e.g., 5s, 10m, 1h)")
    async def set_all_slowmode(self, interaction: discord.Interaction, cooldown: str):
        guild = interaction.guild
        cooldown_seconds = self.parse_cooldown(cooldown)

        await interaction.response.send_message(f"Setting Slowmode in all channels. Cooldown: {cooldown}", ephemeral=True)
        if cooldown_seconds is None or cooldown_seconds > 21600:  
            await interaction.followup.send("Invalid cooldown. Please provide a valid cooldown (Max: 6 hours).", ephemeral=True)
            return

        for channel in guild.text_channels:
            await channel.edit(slowmode_delay=cooldown_seconds)

        await interaction.followup.send(f"Slowmode set in all channels.", ephemeral=True)

    disable_group = app_commands.Group(name="disable", description="Disable slowmode in channels.", parent=slowmode_commands_group)

    @disable_group.command(name="channel", description="Disable slowmode in a specific channel.")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(channel="Select the channel to disable slowmode")
    async def disable_channel_slowmode(self, interaction: discord.Interaction, channel: discord.TextChannel):
        # Check  current slowmode delay of channel
        if channel.slowmode_delay == 0:
            await interaction.response.send_message(f"Slowmode is not active in {channel.mention}.", ephemeral=True)
            return
        
        await channel.edit(slowmode_delay=0)
        await interaction.response.send_message(f"Slowmode has been disabled in {channel.mention}.", ephemeral=True)

    @disable_group.command(name="all", description="Disable slowmode in all channels.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def disable_all_slowmodes(self, interaction: discord.Interaction):
        guild = interaction.guild
        await interaction.response.send_message("Slowmode is being disabled in all channels.", ephemeral=True)
        for channel in guild.text_channels:
            await channel.edit(slowmode_delay=0)
        await interaction.followup.send("Slowmode has been disabled in all channels.", ephemeral=True)

    def parse_cooldown(self, cooldown: str) -> int:
        if cooldown.endswith('s'):
            return int(cooldown[:-1]) 
        elif cooldown.endswith('m'):
            return int(cooldown[:-1]) * 60 
        elif cooldown.endswith('h'):
            return int(cooldown[:-1]) * 3600 
        else:
            return None  

async def setup(bot: commands.Bot):
    await bot.add_cog(SlowmodeCog(bot))
