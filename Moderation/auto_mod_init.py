from discord import app_commands, ui
import discord
from discord.ext import commands

moderationSession = []
userViolationCount = {}

class ModerationOptions(discord.ui.Select):
    def __init__(self, default_values=None, main_interaction: discord.Interaction = None):
        # TO-DO ADD DESCRIPTIONS FOR THE OPTIONS
        options = [
            discord.SelectOption(label="Profanity Filter", value="profanity", default="profanity" in default_values, description="Automatically detect and filter out profane language."),
            discord.SelectOption(label="Spam Filter", value="spam", default="spam" in default_values, description="Identify and mitigate spam messages."),
            discord.SelectOption(label="Capslock Filter", value="capslock", default="capslock" in default_values, description="Monitor and control excessive use of caps-lock in messages."),
            discord.SelectOption(label="Links Filter", value="linkfilter", default="linkfilter" in default_values, description="Control links/invites sharing. (Ignores whitelisted)"),
            discord.SelectOption(label="Temporary Ban", value="tempban", default="tempban" in default_values, description="Ban users who repeatedly violate server rules for 24 hours."),
        ]
        super().__init__(placeholder="Select moderation features...", options=options, min_values=0, max_values=len(options))
        self.main_interaction = main_interaction

    async def callback(self, interaction: discord.Interaction):
        global moderationSession
        selected_values = self.values
        moderationSession = selected_values

        all_features = ["profanity", "spam", "capslock", "linkfilter", "tempban"]
        active_features = [feature for feature in all_features if feature in moderationSession]
        inactive_features = [feature for feature in all_features if feature not in moderationSession]

        embed = discord.Embed(
            title="Moderation Settings Updated",
            color=discord.Color.dark_orange() if moderationSession else discord.Color.brand_red()
        )
        embed.add_field(name="Active Features", value=', '.join(active_features) if active_features else "None", inline=False)
        embed.add_field(name="Inactive Features", value=', '.join(inactive_features) if inactive_features else "None", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=20)
        await self.main_interaction.delete_original_response()

class ModerationView(discord.ui.View):
    def __init__(self, original_interaction):
        super().__init__()
        self.original_interaction = original_interaction
        self.add_item(ModerationOptions(default_values=moderationSession, main_interaction=self.original_interaction))

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    moderation_group = app_commands.Group(name="moderation", description="Moderate community using moderation functions")

    @moderation_group.command(name='set', description="Set auto moderation functions")
    @app_commands.checks.has_permissions(administrator=True)  # Restrict to admin users
    async def start_command(self, interaction: discord.Interaction):
        view = ModerationView(original_interaction=interaction)
        await interaction.response.send_message(
            content="Select the moderation features you want to enable:",
            view=view
        )

    @moderation_group.command(name='stop', description="Disable all moderation functions")
    @app_commands.checks.has_permissions(administrator=True)  # Restrict to admin users
    async def stop_command(self, interaction: discord.Interaction):
        global moderationSession
        moderationSession = []

        embed = discord.Embed(
            title="Moderation Settings Updated",
            color=discord.Color.brand_red()
        )
        embed.add_field(name="Active Features", value="None", inline=False)
        embed.add_field(name="Inactive Features", value="Profanity Filter, Spam Filter, Capslock Filter, Links Filter, Temporary Ban", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=20)
        
async def setup(bot: commands.Bot):
    await bot.add_cog(ModerationCog(bot))
    await bot.tree.sync()