import discord
from discord.ext import commands
from discord import app_commands
from system.whitelist import white_listed_urls

class WhitelistCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # Command group definition
    whitelist_group = app_commands.Group(
        name="whitelist",
        description="Manage whitelisted domains or URLs."
    )

    @whitelist_group.command(name="add", description="Add a URL to the whitelist.")
    async def add_url(self, interaction: discord.Interaction, url: str):

        if url in white_listed_urls:
            await interaction.response.send_message(
                f"🚫 The URL `{url}` is already whitelisted.", ephemeral=True
            )
            return

        white_listed_urls.append(url)
        await interaction.response.send_message(
            f"✅ The URL `{url}` has been added to the whitelist.", ephemeral=True
        )

    @whitelist_group.command(name="show", description="Show all whitelisted URLs.")
    async def show_urls(self, interaction: discord.Interaction):
 
        if not white_listed_urls:
            await interaction.response.send_message(
                "ℹ️ No URLs have been whitelisted yet.", ephemeral=True
            )
            return

        whitelist_display = "\n".join(self.white_listed_urls)
        await interaction.response.send_message(
            f"✅ **Whitelisted URLs:**\n{whitelist_display}", ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(WhitelistCog(bot))
