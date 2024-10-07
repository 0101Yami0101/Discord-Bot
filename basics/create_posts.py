import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
import aiohttp
import urllib.parse

class CreatePostsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.create_group = bot.tree.get_command('create')
        self.add_posts_commands()
        self.image_folder = "data/images"

        if not os.path.exists(self.image_folder):
            os.makedirs(self.image_folder)

    def add_posts_commands(self):
        @self.create_group.command(
            name="post", 
            description="Create a post in a forum channel."
        )
        async def create_forum_post(interaction: discord.Interaction):
           
            forum_channels = [channel for channel in interaction.guild.channels if isinstance(channel, discord.ForumChannel)]  # Forum channels

            if not forum_channels:
                await interaction.response.send_message("No forum channels available. Please create one first.", ephemeral=True)
                return

            # Dropdown for selecting forum channel
            forum_select = discord.ui.Select(
                placeholder="Select a forum channel...",
                options=[discord.SelectOption(label=channel.name, value=str(channel.id)) for channel in forum_channels]
            )

            async def select_callback(select_interaction: discord.Interaction):
                selected_channel_id = int(select_interaction.data['values'][0])
                selected_forum_channel = discord.utils.get(interaction.guild.channels, id=selected_channel_id)

                await interaction.delete_original_response()

                await select_interaction.response.send_message("Please provide the title for the post.", ephemeral=True)

                def check(m):
                    return m.author == interaction.user and m.channel == interaction.channel

                try:
                    # Get the title
                    title_response = await self.bot.wait_for('message', check=check, timeout=60)
                    title = title_response.content
                    await title_response.delete(delay=3)

                    # Get the description
                    await interaction.followup.send("Now provide the description for the post.", ephemeral=True)
                    description_response = await self.bot.wait_for('message', check=check, timeout=60)
                    description = description_response.content
                    await description_response.delete(delay=3)

                    # Ask for an image (or skip)
                    await interaction.followup.send("Would you like to add an image? Reply with the URL or attach an image, or type 'skip' to skip this step.", ephemeral=True)
                    image_response = await self.bot.wait_for('message', check=check, timeout=60)

                    embed = discord.Embed(title=title, description=description, color=discord.Color.blue())

                    img_path = None
                    file = None
                    if image_response.content.lower() != 'skip':
                        if image_response.attachments:  # Attachment provided
                            attachment = image_response.attachments[0]
                            image_url = attachment.url

                            # Download image and save it locally
                            async with aiohttp.ClientSession() as session:
                                async with session.get(image_url) as img_response:
                                    if img_response.status == 200:
                                        img_data = await img_response.read()
                                        img_path = os.path.join(self.image_folder, attachment.filename)
                                        with open(img_path, 'wb') as img_file:
                                            img_file.write(img_data)

                            # Attach the image properly
                            file = discord.File(img_path, filename=attachment.filename)
                            embed.set_image(url=f"attachment://{attachment.filename}")
                            await image_response.delete()

                        else:  # URL provided
                            image_url = image_response.content
                            print(image_url)
                            if self.is_valid_url(image_url):  # Validate the URL

                                embed.set_image(url=image_url)
                                await image_response.delete()
                            else:
                                await interaction.followup.send("Invalid URL. Please restart the process with a valid image URL or attachment.", ephemeral=True)
                                return


                    if file:
                        thread = await selected_forum_channel.create_thread(name=title, content=None, embed=embed, file=file)
                    else:
                        thread = await selected_forum_channel.create_thread(name=title, content=None, embed=embed)

                    await interaction.followup.send(f"Post created successfully in {selected_forum_channel.mention}.", ephemeral=True)

                    # Delete the image 
                    if img_path and os.path.exists(img_path):
                        os.remove(img_path)

                except asyncio.TimeoutError:
                    await interaction.followup.send("You took too long to respond, post creation has been cancelled.", ephemeral=True)

            forum_select.callback = select_callback

            view = discord.ui.View()
            view.add_item(forum_select)

            await interaction.response.send_message("Please select a forum channel to post in:", view=view, ephemeral=True)

    def is_valid_url(self, url: str) -> bool:
        parsed_url = urllib.parse.urlparse(url)
        return all([parsed_url.scheme, parsed_url.netloc, parsed_url.path])

async def setup(bot: commands.Bot):
    await bot.add_cog(CreatePostsCog(bot))
