import discord
from discord import app_commands
from discord.ext import commands

class KickCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a member from the server.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick_member(self, interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):

        guild = interaction.guild
        member = guild.get_member(user.id)
        
        if member:
            try:
                await member.kick(reason=reason)
                await interaction.response.send_message(f"{user.mention} has been kicked from the server.\nReason: {reason}", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message(f"Unable to kick {user.mention}. I may not have the necessary permissions.", ephemeral=True)
        else:
            await interaction.response.send_message(f"{user.mention} is not in the server.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(KickCog(bot))
