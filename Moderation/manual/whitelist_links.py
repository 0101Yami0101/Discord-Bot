import discord
from discord import app_commands

white_listed_urls = []

@app_commands.command(name="whitelist", description="Whitelist a domain or URL")
async def whitelist_url(interaction: discord.Interaction, url: str):
   
    if url in white_listed_urls:
        await interaction.response.send_message(f"🚫 The URL `{url}` is already whitelisted.", ephemeral=True)
        return


    white_listed_urls.append(url)
    

    await interaction.response.send_message(f"✅ The URL `{url}` has been added to the whitelist.", ephemeral=True)
