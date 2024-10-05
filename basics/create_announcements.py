import discord
from discord import app_commands
from discord.ext import commands
import asyncio

class CreateAnnouncementCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.create_group = bot.tree.get_command('create')
        self.add_announcements_commands()

    def add_announcements_commands(self):  
        @self.create_group.command(
            name="announcement", 
            description="Create an announcement with optional image."
        )
        @app_commands.describe(
        title='The title for the announcement.',
        description='The description for the announcement.',
        add_image='Select "True" to add an image (attachment or URL), or "False" to skip adding an image.',
        mentions='Optional: Mention members in the announcement. (Demo: @<USERNAME>)')
        async def create_announcement(
            interaction: discord.Interaction, 
            title: str, 
            description: str, 
            add_image: bool,  # User will select True or False
            mentions: str = None
        ):
           
            border = "═" * 33
            decorated_title = f"📢📢📢📢📢✨ **ANNOUNCEMENT** ✨📢📢📢📢📢\n{border}\n\n**{title}**"
            
            if mentions:
                full_description = f"{mentions}\n\n{description}"
            else:
                full_description = description

            embed = discord.Embed(
                title=decorated_title,
                description=full_description, 
                color=discord.Color.blurple()
            )

           
            guild_name = interaction.guild.name
            embed.set_footer(text=f"⚙️ {guild_name}", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)

          
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url)

           
            allowed_mentions = discord.AllowedMentions(users=True, roles=True, everyone=True)

           
            announcement_channel = discord.utils.get(interaction.guild.channels, name="announcements")
            if announcement_channel is None:
                announcement_channel = interaction.channel

            if add_image:
 
                await interaction.response.send_message(
                    "Please upload an image or send an image URL (jpg, jpeg, png etc.).", ephemeral=True
                )

                def check(m):
                    return m.author == interaction.user and m.channel == interaction.channel
                
                try:
                   
                    image_response = await self.bot.wait_for('message', check=check, timeout=60)
                    if image_response.attachments:
      
                        embed.set_image(url=image_response.attachments[0].url)
                    else:
                
                        embed.set_image(url=image_response.content)

                except asyncio.TimeoutError:
                    await interaction.followup.send("You took too long to respond, no image will be added.", ephemeral=True)

            await announcement_channel.send(embed=embed, allowed_mentions=allowed_mentions)
            await interaction.followup.send(f"Announcement created in {announcement_channel.mention}", ephemeral=True)

            if 'image_response' in locals():
                await image_response.delete(delay=1)

# Setup the cog
async def setup(bot: commands.Bot):
    await bot.add_cog(CreateAnnouncementCog(bot))
