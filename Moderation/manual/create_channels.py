import discord
from discord import app_commands
from discord.ext import commands

class CreateChannelsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    create_group = app_commands.Group(name="create", description="Create anything (Channels, roles, announcements, embeds, reminders etc).")
    create_channels_group = app_commands.Group(name="channel", description="Create channels (Text, Voice, Forum, Announcement, or Stage).", parent=create_group)

    @create_channels_group.command(name="text", description="Create a text channel (private or public).")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(channel_name="Enter the channel name", is_private="Is the channel private?", category="Select the category to create the channel", topic="Optional: Enter the topic for the channel")
    async def create_text_channel(self, interaction: discord.Interaction, channel_name: str, is_private: bool, topic: str = None, category: discord.CategoryChannel = None):
        await self.create_channel(interaction, channel_name, discord.ChannelType.text, is_private, topic, category)

    @create_channels_group.command(name="voice", description="Create a voice channel (private or public).")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(channel_name="Enter the channel name", is_private="Is the channel private?", category="Select the category to create the channel", topic="Optional: Enter the topic for the channel")
    async def create_voice_channel(self, interaction: discord.Interaction, channel_name: str, is_private: bool, topic: str = None, category: discord.CategoryChannel = None):
        await self.create_channel(interaction, channel_name, discord.ChannelType.voice, is_private, topic, category)

    @create_channels_group.command(name="forum", description="Create a forum channel (private or public).")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(channel_name="Enter the channel name", is_private="Is the channel private?", category="Select the category to create the channel", topic="Optional: Enter the topic for the channel")
    async def create_forum_channel(self, interaction: discord.Interaction, channel_name: str, is_private: bool, topic: str = None, category: discord.CategoryChannel = None):
        await self.create_channel(interaction, channel_name, discord.ChannelType.forum, is_private, topic, category)

    @create_channels_group.command(name="announcement", description="Create an announcement channel (private or public).")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(channel_name="Enter the channel name", is_private="Is the channel private?", category="Select the category to create the channel", topic="Optional: Enter the topic for the channel")
    async def create_announcement_channel(self, interaction: discord.Interaction, channel_name: str, is_private: bool, topic: str = None, category: discord.CategoryChannel = None):
        await self.create_channel(interaction, channel_name, discord.ChannelType.news, is_private, topic, category)

    @create_channels_group.command(name="stage", description="Create a stage channel (private or public).")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(channel_name="Enter the channel name", is_private="Is the channel private?", category="Select the category to create the channel", topic="Optional: Enter the topic for the channel")
    async def create_stage_channel(self, interaction: discord.Interaction, channel_name: str, is_private: bool, topic: str = None, category: discord.CategoryChannel = None):
        await self.create_channel(interaction, channel_name, discord.ChannelType.stage_voice, is_private, topic, category)

    async def create_channel(self, interaction: discord.Interaction, channel_name: str, channel_type: discord.ChannelType, is_private: bool, topic: str, category: discord.CategoryChannel = None):
        guild = interaction.guild

        if category is None:
            category = interaction.channel.category

        overwrites = {}  # Roles if the channel is private
        if is_private:
            roles = guild.roles
            role_select_options = [discord.SelectOption(label=role.name, value=str(role.id)) for role in roles if role != guild.default_role]

            # Dropdown
            role_select = discord.ui.Select(
                placeholder="Select roles",
                min_values=1,
                max_values=len(roles) - 1,  # Maximum number of roles user can select
                options=role_select_options
            )

            await interaction.response.defer(ephemeral=True)

            view = discord.ui.View()
            view.add_item(role_select)

            async def role_callback(interaction: discord.Interaction):
                selected_roles = [guild.get_role(int(role_id)) for role_id in role_select.values]
                for role in selected_roles:
                    overwrites[role] = discord.PermissionOverwrite(view_channel=True)

                overwrites[guild.default_role] = discord.PermissionOverwrite(view_channel=False)

                await self.finalize_channel_creation(interaction, guild, channel_name, channel_type, is_private, topic, overwrites, category)
                await interaction.delete_original_response()

            role_select.callback = role_callback
            await interaction.followup.send("Select the roles for the private channel.", view=view, ephemeral=True)

        else:
            await self.finalize_channel_creation(interaction, guild, channel_name, channel_type, is_private, topic, overwrites, category)

    # Finalize Channel Creation
    async def finalize_channel_creation(self, interaction: discord.Interaction, guild: discord.Guild, channel_name: str, channel_type: discord.ChannelType, is_private: bool, topic: str, overwrites: dict, category: discord.CategoryChannel):
        await interaction.response.defer(ephemeral=True)

        try:
            created_channel = None
            if channel_type == discord.ChannelType.text:
                created_channel = await guild.create_text_channel(
                    name=channel_name,
                    overwrites=overwrites if overwrites else {},
                    category=category,
                    topic=topic 
                )
            elif channel_type == discord.ChannelType.voice:
                created_channel = await guild.create_voice_channel(
                    name=channel_name,
                    overwrites=overwrites if overwrites else {},
                    category=category
                )
            elif channel_type == discord.ChannelType.stage_voice:
                created_channel = await guild.create_stage_channel(
                    name=channel_name,
                    overwrites=overwrites if overwrites else {},
                    category=category
                )
            elif channel_type == discord.ChannelType.news:
                created_channel = await guild.create_text_channel(
                    name=channel_name,
                    overwrites=overwrites if overwrites else {},
                    category=category,
                    news=True,
                    topic=topic 
                )
            elif channel_type == discord.ChannelType.forum:
                created_channel = await guild.create_forum(
                    name=channel_name,
                    overwrites=overwrites if overwrites else {},
                    category=category,
                    topic=topic  
                )

            if created_channel:
                message = f"{channel_type.name.capitalize()} channel '{created_channel.mention}' has been created in category {category.name.upper() if category else 'default category'}."

                if is_private:
                    message += "\n📝 Note: Custom permissions are not set for selected roles."
                await interaction.followup.send(message, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"Channel creation failed. {e}. Try again.")


async def setup(bot: commands.Bot):
    await bot.add_cog(CreateChannelsCog(bot))
