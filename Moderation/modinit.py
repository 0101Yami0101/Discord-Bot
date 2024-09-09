from discord import app_commands
import discord

moderationSession = []

@app_commands.command(name='moderation', description="Set auto moderation functions")
@app_commands.describe(all="Selecting this option TRUE will set all functions to TRUE")
@app_commands.checks.has_permissions(administrator=True)  # Restrict to admin users
async def mod_command(
    interaction: discord.Interaction,
    all: bool = False,
    profanity: bool = False,
    spam: bool = False
):
    global moderationSession

    if all:
        # If 'all' is selected, enable all features and ignore other options
        moderationSession = ["profanity", "spam"]
        profanity = False  # Ignore profanity parameter
        spam = False       # Ignore spam parameter
    else:
        # Set features based on individual boolean parameters
        moderationSession = []
        if profanity:
            moderationSession.append("profanity")
        if spam:
            moderationSession.append("spam")

    await interaction.response.send_message(embed=discord.Embed(
        title="Moderation Settings Updated",
        description=f"Selected Features: {', '.join(moderationSession) if moderationSession else 'None'}",
        color=discord.Color.dark_orange() if moderationSession else discord.Color.brand_red()
    ))
