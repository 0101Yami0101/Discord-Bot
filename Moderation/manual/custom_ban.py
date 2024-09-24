import discord
from discord import app_commands
from discord.ext import commands
import asyncio

class CustomBanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Create a command group for banning users
    custom_ban_group = app_commands.Group(name="ban", description="Ban a user for a set time or permanently.")

    # Ban a specific member for a custom time or permanently
    @custom_ban_group.command(name="member", description="Ban a member from the server for a custom duration (Permanent if no duration given).")
    @app_commands.describe(user='The user that you want to ban', duration='The duration of the mute (e.g., 5m for 5 minutes or 2h for 2 hours)')
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban_member(self, interaction: discord.Interaction, user: discord.User, duration: str = None):
        guild = interaction.guild

        # Ban the user
        try:
            
            await guild.ban(user, reason="Custom ban command", delete_message_days=0)
            await interaction.response.send_message(f"{user.mention} has been banned", ephemeral=True)

            if duration:
                # Parse duration (e.g., 2m for minutes, 2h for hours, 2d for days)
                seconds = self.parse_duration(duration)
                if seconds:
                    await interaction.followup.send(f"{user.mention} will be unbanned in {duration}.", ephemeral=True)
                    await asyncio.sleep(seconds)
                    await guild.unban(user)
                    await interaction.followup.send(f"{user.mention} has been unbanned after {duration}.", ephemeral=True)
                else:
                    await interaction.followup.send(f"Invalid duration format. {user.mention} will remain banned permanently.", ephemeral=True)
            else:
                await interaction.followup.send(f"{user.mention} is banned permanently.", ephemeral=True)
        except Exception as e:
            await interaction.response.send("Can't ban this user due to lack of permissions.")

    # Helper function to parse the duration string
    def parse_duration(self, duration: str) -> int:
        if duration.endswith('m'):
            return int(duration[:-1]) * 60  # Convert minutes to seconds
        elif duration.endswith('h'):
            return int(duration[:-1]) * 3600  # Convert hours to seconds
        elif duration.endswith('d'):
            return int(duration[:-1]) * 86400  # Convert days to seconds
        else:
            return None

# Add this cog to your bot
async def setup(bot: commands.Bot):
    await bot.add_cog(CustomBanCog(bot))
