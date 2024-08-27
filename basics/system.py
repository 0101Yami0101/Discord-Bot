import discord
from discord import app_commands
from discord.ext import commands

# Define app commands in the separate file

@app_commands.command(name="info", description="Get server and user information.")
async def info(interaction: discord.Interaction):
    server = interaction.guild
    member = interaction.user
    info_message = (
        f"Server name: {server.name}\n"
        f"Server ID: {server.id}\n"
        f"Your name: {member.name}\n"
        f"Your ID: {member.id}\n"
        f"Total members: {server.member_count}"
    )
    await interaction.response.send_message(info_message)



@app_commands.command(name="avatar", description="Show a discord user's avatar (Your's by default)")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    await interaction.response.send_message(member.avatar.url)
