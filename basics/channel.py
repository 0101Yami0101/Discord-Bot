import discord
from discord import app_commands
from discord.ext import commands

CHANNEL_PERMISSIONS_LIST = [
    'view_channel', 'manage_channels', 'manage_permissions', 'send_messages',
    'send_tts_messages', 'manage_messages', 'embed_links', 'attach_files',
    'read_message_history', 'mention_everyone', 'use_external_emojis',
    'view_guild_insights', 'connect', 'speak', 'mute_members', 'deafen_members',
    'move_members', 'use_vad', 'change_nickname', 'manage_nicknames',
    'manage_roles', 'manage_webhooks', 'use_application_commands',
    'request_to_speak', 'manage_events', 'manage_threads', 'create_public_threads',
    'create_private_threads', 'use_external_stickers', 'send_messages_in_threads',
    'use_embedded_activities', 'moderate_members', 'use_soundboard', 'send_voice_messages',
    'send_polls', 'use_external_apps'
]

def chunk_permissions(permissions_list, chunk_size=25):
    for i in range(0, len(permissions_list), chunk_size):
        yield permissions_list[i:i + chunk_size]

class ChannelRolePermissionView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, channel: discord.abc.GuildChannel):
        super().__init__(timeout=180)
        self.interaction = interaction
        self.channel = channel
        self.prev_followup = None
        self.temp_result = []  
        self.final_result = [] 

        #dropdowns 
        for index, chunk in enumerate(chunk_permissions(CHANNEL_PERMISSIONS_LIST)):
            options = [discord.SelectOption(label=perm) for perm in chunk]
            select = discord.ui.Select(
                placeholder=f"Select channel permissions (Part {index + 1})",
                min_values=0,
                max_values=len(chunk),
                options=options,
                custom_id=f"channel_permissions_select_{index}"
            )
            select.callback = self.handle_selection
            self.add_item(select)

    async def handle_selection(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        self.temp_result = []
        for child in self.children:
            if isinstance(child, discord.ui.Select):
                self.temp_result.extend(child.values)

        if self.prev_followup is not None:
            await self.prev_followup.delete()

        self.prev_followup = await interaction.followup.send(
            f"📝 **Selected Permissions:**\n" + '\n'.join([f"👉 {perm}" for perm in self.temp_result]), 
            ephemeral=True
        )

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit(self, interaction: discord.Interaction, button):
        self.final_result = self.temp_result.copy() if self.temp_result else None

        if self.prev_followup:
            await self.prev_followup.delete()

        await interaction.response.defer(ephemeral=True)
        await interaction.delete_original_response()
        self.stop()

class ChannelPermissions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_group = bot.tree.get_command('channel')
        self.add_channel_commands()

    def add_channel_commands(self):
        @self.channel_group.command(
            name="permissions", 
            description="Set CHANNEL-SPECIFIC permissions for a role in any channel (text, voice, or category)."
        )
        @app_commands.describe(
            channel="The channel where you want to set permissions (text, voice, or category).",
            role="The role whose permissions will be set."
        )
        async def set_channel_permissions(
            interaction: discord.Interaction, channel: discord.abc.GuildChannel, role: discord.Role
        ):
            view = ChannelRolePermissionView(interaction, channel)
            await interaction.response.send_message(
                f"⚙️ Please select permissions for the role `{role.name}` in `{channel.name}`:\n\n"
                f"📝 **Note:** This will overwrite all previously set permissions for the selected in the `{channel.name}` channel.", 
                view=view, ephemeral=True
            )

            await view.wait()

            if not view.final_result:
                return

            #PermissionOverwrite instance
            overwrite = discord.PermissionOverwrite()

            # Set
            for perm in view.final_result:
                setattr(overwrite, perm, True)

            # Apply
            try:
                await channel.set_permissions(role, overwrite=overwrite)
                await interaction.followup.send(
                    f"✅ Permissions for role `{role.name}` in `{channel.name}` have been updated.\n"
                    f"**Added Permissions:**\n" + '\n'.join([f"✅ {perm}" for perm in view.final_result]), 
                    ephemeral=True
                )
            except discord.Forbidden:
                await interaction.followup.send(
                    "❌ You do not have permission to modify channel permissions.", 
                    ephemeral=True
                )

async def setup(bot: commands.Bot):
    await bot.add_cog(ChannelPermissions(bot))
