import discord
from discord.ext import commands
from discord import app_commands

class InfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="info", description="Get server and user information.")
    @discord.app_commands.default_permissions(administrator=True)
    async def info(self, interaction: discord.Interaction, user: discord.Member = None):
        if user is None:
            user = interaction.user


        if user != interaction.user and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to view other users' information.", ephemeral=True)
            return

        info_message = (
            f"Server name: {interaction.guild.name}\n"
            f"Server ID: {interaction.guild.id}\n"
            f"Your name: {interaction.user.name}\n"
            f"Your ID: {interaction.user.id}\n"
            f"Total members: {interaction.guild.member_count}\n"
        )

        if user != interaction.user: 
            info_message += (
                f"\n{user.name}'s Information:\n"
                f"Username: {user.name}\n"
                f"User ID: {user.id}\n"
                f"Join date: {user.joined_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Roles: {', '.join([role.name for role in user.roles if role.name != '@everyone'])}\n"
            )
        else: 
            info_message += (
                f"\nYour Join Date: {user.joined_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Your Roles: {', '.join([role.name for role in user.roles if role.name != '@everyone'])}\n"
            )


        await interaction.response.send_message(info_message)

    @app_commands.command(name="avatar", description="Show a Discord user's avatar (Your's by default).")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        embed = discord.Embed(
            title=f"{member.name}'s Avatar",
            color=discord.Color.blue()
        )
        embed.set_image(url=avatar_url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roleinfo", description="Get information about a specific role.")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        embed = discord.Embed(
            title=f"Role Information: {role.name}",
            color=role.color
        )
        embed.add_field(name="Role ID", value=role.id, inline=True)
        embed.add_field(name="Color", value=str(role.color), inline=True)
        embed.add_field(name="Position", value=role.position, inline=True)
        embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No", inline=True)
        embed.add_field(name="Hoisted", value="Yes" if role.hoist else "No", inline=True)
        embed.add_field(name="Members", value=len(role.members), inline=True)
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(InfoCog(bot))
