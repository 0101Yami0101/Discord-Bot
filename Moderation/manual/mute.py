import discord
from discord import app_commands
from discord.ext import commands
import asyncio

class MuteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.muted_members = set()  

    async def cog_load(self):
        # Scan for muted members 
        for guild in self.bot.guilds:
            mute_role = discord.utils.get(guild.roles, name="Muted")
            if mute_role:
                for member in guild.members:
                    if mute_role in member.roles:
                        self.muted_members.add(member.id)

    async def cog_load_hook(self):  
        await self.cog_load()

    mute_commands_group = app_commands.Group(name="mute", description="Mute, unmute, and list muted members.")

    @mute_commands_group.command(name="user", description="Mute a specific user for a given duration.")
    @app_commands.describe(user="The user you want to mute", duration="The duration of the mute (e.g., 5m for 5 minutes or 2h for 2 hours)")
    @app_commands.checks.has_permissions(administrator=True)
    async def mute_member(self, interaction: discord.Interaction, user: discord.User, duration: str):

        guild = interaction.guild
        member = guild.get_member(user.id)
        mute_role = discord.utils.get(guild.roles, name="Muted")

        if not mute_role:
            # If there isn't a "Muted" role, create it
            mute_role = await guild.create_role(name="Muted", reason="Mute role for muting users")
            for channel in guild.channels:
                # Set permissions: only allow viewing channels, no sending messages or speaking
                await channel.set_permissions(mute_role, speak=False, send_messages=False, add_reactions=False, 
                                               view_channel=True, read_message_history=True)

        if mute_role in member.roles:
            await interaction.response.send_message(f'{user.mention} is already muted!', ephemeral=True)
        else:
            await member.add_roles(mute_role)
            await interaction.response.send_message(f'{user.mention} has been muted for {duration}', ephemeral=True)
            
            await member.send(f'You have been muted in {guild.name}.')

            self.muted_members.add(user.id)  # Track muted member


            seconds = self.parse_duration(duration)
            if seconds:
                await asyncio.sleep(seconds)
                await self.unmute_member_auto(interaction.guild, member)

    async def unmute_member_auto(self, guild, member):

        mute_role = discord.utils.get(guild.roles, name="Muted")
        if mute_role and mute_role in member.roles:
            await member.remove_roles(mute_role)
            self.muted_members.discard(member.id)

            await member.send(f'You have been unmuted in {guild.name}.')

    @mute_commands_group.command(name="unmute", description="Unmute a specific user.")
    @app_commands.checks.has_permissions(administrator=True)
    async def unmute_member(self, interaction: discord.Interaction, user: discord.User):
        guild = interaction.guild
        member = guild.get_member(user.id)
        mute_role = discord.utils.get(guild.roles, name="Muted")

        if mute_role and mute_role in member.roles:
            await member.remove_roles(mute_role)
            self.muted_members.discard(user.id)  
            await interaction.response.send_message(f'{user.mention} has been unmuted', ephemeral=True)
        else:
            await interaction.response.send_message(f'{user.mention} is not muted!', ephemeral=True)

    @mute_commands_group.command(name="list", description="List all muted members.")
    @app_commands.checks.has_permissions(administrator=True)
    async def list_muted_members(self, interaction: discord.Interaction):
        guild = interaction.guild
        muted_members_list = []

        for user_id in self.muted_members:
            member = guild.get_member(user_id)
            if member:
                muted_members_list.append(member.mention)

        if muted_members_list:
            muted_members = ", ".join(muted_members_list)
            await interaction.response.send_message(f"Muted members: {muted_members}", ephemeral=True)
        else:
            await interaction.response.send_message("No members are currently muted.", ephemeral=True)

    def parse_duration(self, duration: str) -> int:
 
        if duration.endswith('m'):
            return int(duration[:-1]) * 60 
        elif duration.endswith('h'):
            return int(duration[:-1]) * 3600  
        else:
            return None  

async def setup(bot: commands.Bot):
    await bot.add_cog(MuteCog(bot))
