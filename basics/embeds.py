import discord
from discord.ext import commands
from discord.ui import View, Button
import traceback
import datetime
import asyncio

# Track each user's active modal instance separately
user_modals = {}
interaction_buttons = None


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

        # Add the inputs to the modal
        self.add_item(self.name)
        self.add_item(self.desc)
        self.add_item(self.link)

    async def on_submit(self, interaction: discord.Interaction):
        global user_modals, interaction_buttons, interaction_msg
        user_modals[self.user_id] = self

        # Add img or skip button
        add_img = Button(label="Add Image", style=discord.ButtonStyle.blurple, custom_id="add_image")
        skip = Button(label="Skip", style=discord.ButtonStyle.secondary, custom_id="skip_upload")

        view = View()
        view.add_item(add_img)
        view.add_item(skip)
        
        await interaction.response.send_message('Add an image?', ephemeral=True, delete_after=10)
        interaction_buttons = await interaction.followup.send(view=view, ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(f'Oops! Something went wrong. Error: {str(error)}', ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)


@commands.command(name="embed", description="Create Embed")
async def create_embed(ctx):
    await ctx.message.delete()
    create_button = Button(label="Create Embed", style=discord.ButtonStyle.red, custom_id="create_embed")
    view = View()
    view.add_item(create_button)
    await ctx.channel.send("Click the button to create a custom embed", view=view)


# Handler for button interactions
async def on_buttons_interaction(interaction):
    global user_modals, interaction_buttons, interaction_msg

    user_id = interaction.user.id

    if interaction.data["custom_id"] == "create_embed":  
        modal = EmbedModal(user_id=user_id)
        user_modals[user_id] = modal
        await interaction.message.delete()
        await interaction.response.send_modal(modal)

    elif interaction.data["custom_id"] == "add_image":
        if user_id in user_modals and user_modals[user_id] is not None:
            user_modals[user_id].creatorTracker = interaction.user.id
            await interaction_buttons.delete() #Remove buttons
            await interaction.response.send_message("Upload an image from your system", ephemeral=True, delete_after=30)
        else:
            await interaction.response.send_message("No active modal found. Please try creating a new embed.", ephemeral=True, delete_after=20)

    elif interaction.data["custom_id"] == "skip_upload":
        
            
        await interaction.response.send_message("Creating..", ephemeral=True, delete_after=8)
        modal = user_modals.get(user_id)
        embed = await send_custom_embed(modal)
        if embed:
            # SEND EMBED
            await interaction.channel.send(embed=embed)
            await interaction_buttons.delete() #Remove buttons
            user_modals[user_id] = None  # Reset modal for user
            return
        else:
            await interaction.channel.send("Failed to create embed.", ephemeral=True, delete_after=30)


# Handler for image upload messages
async def on_attachment_upload_message(message):
    global user_modals

    if message.author.bot:
        return
    if not message.attachments:
        return

    user_id = message.author.id
    modal = user_modals.get(user_id)

    if modal is None:
        return

    if modal.creatorTracker is not None and message.author.id == modal.creatorTracker:
        for attachment in message.attachments:
            if (attachment.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif')) or
                (attachment.content_type and 'image' in attachment.content_type)):
                modal.image = attachment.url  # Store the image URL in the modal instance
                try:
                    embed = await send_custom_embed(modal)
                    await message.channel.send("Creating..", delete_after=5)
                    await message.channel.send(embed=embed)
                    await asyncio.sleep(2)
                    await message.delete()
                    
                    user_modals[user_id] = None  # Reset modal for user
                    return
                except Exception as e:
                    print(f"Error sending message: {e}")
                return
            else:
                await message.channel.send("Please upload an image.")


# Custom embed creation function
async def send_custom_embed(mdl):
    if mdl is None:
        return None
    
    embed = discord.Embed(
        title=mdl.name.value,
        description=mdl.desc.value,
        url=mdl.link.value if mdl.link.value else None,
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now()
    )

    if mdl.image is not None:
        embed.set_image(url=mdl.image)

    return embed
