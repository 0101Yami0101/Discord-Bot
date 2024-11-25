import discord
from discord.ext import commands
from discord.ui import View, Button
import traceback
import datetime
import re

class EmbedModal(discord.ui.Modal, title='Embed'):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.name = discord.ui.TextInput(
            label='Title',
            placeholder='Your title here..'
        )
        self.desc = discord.ui.TextInput(
            label='Description',
            style=discord.TextStyle.long,
            placeholder='Body...',
            required=False,
            max_length=300,
        )
        self.link = discord.ui.TextInput(
            label='Link',
            style=discord.TextStyle.long,
            placeholder='Link (if applicable)...',
            required=False,
            max_length=300,
        )
        self.creatorTracker = None
        self.image = None
        self.add_item(self.name)
        self.add_item(self.desc)
        self.add_item(self.link)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Add an image?", ephemeral=True)
        add_img = Button(label="Add Image", style=discord.ButtonStyle.blurple, custom_id="add_image")
        skip = Button(label="Skip", style=discord.ButtonStyle.secondary, custom_id="skip_upload")
        view = View()
        view.add_item(add_img)
        view.add_item(skip)
        await interaction.followup.send(view=view, ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(f'Oops! Something went wrong: {str(error)}', ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)


class EmbedCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_modals = {}
        self.interaction_buttons = None

    @discord.app_commands.command(name="embed", description="Quickly create a custom embed to display information.")
    @discord.app_commands.default_permissions(administrator=True)
    async def create_embed(self, interaction: discord.Interaction):
        create_button = Button(label="Create Embed", style=discord.ButtonStyle.red, custom_id="create_embed")
        view = View()
        view.add_item(create_button)
        await interaction.response.send_message("Click the button to create a custom embed.", view=view)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if not interaction.data.get("custom_id"):
            return

        if interaction.data["custom_id"] == "create_embed":
            modal = EmbedModal(user_id=user_id)
            self.user_modals[user_id] = modal
            await interaction.response.send_modal(modal)

        elif interaction.data["custom_id"] == "add_image":
            modal = self.user_modals.get(user_id)
            if modal:
                modal.creatorTracker = user_id
                await interaction.response.send_message("Upload an image from your system.", ephemeral=True)
            else:
                await interaction.response.send_message("No active modal found. Please try again.", ephemeral=True)

        elif interaction.data["custom_id"] == "skip_upload":
            modal = self.user_modals.get(user_id)
            if modal:
                try:
                    embed = await self.send_custom_embed(modal)
                    if embed:
                        await interaction.channel.send(embed=embed)
                        self.user_modals[user_id] = None
                    else:
                        await interaction.response.send_message("Failed to create embed.", ephemeral=True)
                except ValueError as e:
                    await interaction.response.send_message(str(e), ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.attachments:
            return

        user_id = message.author.id
        modal = self.user_modals.get(user_id)
        if modal and modal.creatorTracker == user_id:
            for attachment in message.attachments:
                if attachment.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
                    modal.image = attachment.url
                    embed = await self.send_custom_embed(modal)
                    if embed:
                        await message.channel.send(embed=embed)
                        self.user_modals[user_id] = None
                        await message.delete()
                        return
            await message.channel.send("Please upload a valid image.")

    async def send_custom_embed(self, modal: EmbedModal):
        if not modal:
            return None
        
        # Validate URL
        url_pattern = re.compile(r'^(http|https)://[^\s]+$')
        if modal.link.value and not url_pattern.match(modal.link.value):
            raise ValueError("Invalid link provided. Please check the link and try again.")

        embed = discord.Embed(
            title=modal.name.value,
            description=modal.desc.value,
            url=modal.link.value if modal.link.value else None,
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        if modal.image:
            embed.set_image(url=modal.image)
        
        return embed


async def setup(bot: commands.Bot):
    await bot.add_cog(EmbedCog(bot))
