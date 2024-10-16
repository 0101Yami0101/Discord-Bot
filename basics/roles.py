from discord import Permissions, SelectOption, app_commands
from discord.ext import commands
import discord

PERMISSIONS_LIST = [
    'create_instant_invite', 'kick_members', 'ban_members', 'administrator',
    'manage_channels', 'manage_guild', 'add_reactions', 'view_audit_log',
    'priority_speaker', 'stream', 'read_messages', 'send_messages',
    'send_tts_messages', 'manage_messages', 'embed_links', 'attach_files',
    'read_message_history', 'mention_everyone', 'use_external_emojis',
    'view_guild_insights', 'connect', 'speak', 'mute_members', 'deafen_members',
    'move_members', 'use_voice_activation', 'change_nickname', 'manage_nicknames',
    'manage_roles', 'manage_webhooks', 'manage_emojis_and_stickers', 'use_application_commands',
    'request_to_speak', 'manage_events', 'manage_threads', 'create_public_threads',
    'create_private_threads', 'use_external_stickers', 'send_messages_in_threads',
    'use_embedded_activities', 'moderate_members', 'view_creator_monetization_analytics',
    'use_soundboard', 'create_expressions', 'create_events', 'use_external_sounds',
    'send_voice_messages', 'send_polls', 'use_external_apps'
]

def chunk_permissions(permissions_list, chunk_size=25):
    for i in range(0, len(permissions_list), chunk_size):
        yield permissions_list[i:i + chunk_size]


class RoleEditView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, role: discord.Role):
        super().__init__(timeout=180)
        self.interaction = interaction
        self.role = role
        self.prev_followup = None
        self.temp_result = []  
        self.final_result = [] 

        # Populate dropdown
        for index, chunk in enumerate(chunk_permissions(PERMISSIONS_LIST)):
            options = []
            for perm in chunk:
                is_active = getattr(role.permissions, perm, False)
                options.append(discord.SelectOption(label=perm, default=is_active))
            
            select = discord.ui.Select(
                placeholder=f"Select permissions (Part {index + 1})",
                min_values=0,
                max_values=len(chunk),
                options=options,
                custom_id=f"permissions_select_{index}"
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
            f"📝**LIST OF SELECTED PERMISSIONS:**📝\n" + '\n'.join([f"👉 {perm}" for perm in self.temp_result]), ephemeral=True
        )

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit(self, interaction: discord.Interaction, button):
        self.final_result = self.temp_result.copy() if self.temp_result else None
        
        if self.prev_followup:
            await self.prev_followup.delete()

        await interaction.response.defer(ephemeral=True)
        await interaction.delete_original_response()
        self.stop()


class RoleCreationView(discord.ui.View):
    def __init__(self, interaction):
        super().__init__(timeout=180)
        self.interaction = interaction
        self.prev_followup= None
        self.temp_result = []  
        self.final_result = [] 

        for index, chunk in enumerate(chunk_permissions(PERMISSIONS_LIST)):
            select = discord.ui.Select(
                placeholder=f"Select permissions (Part {index + 1})",
                min_values=0,
                max_values=len(chunk),
                options=[discord.SelectOption(label=perm) for perm in chunk],
                custom_id=f"permissions_select_{index}"
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
        self.prev_followup= await interaction.followup.send(f"📝**LIST OF SELECTED PERMISSIONS:**📝\n" + '\n'.join([f"👉 {perm}" for perm in self.temp_result]), ephemeral=True)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit(self, interaction: discord.Interaction, button):
        if not self.temp_result:
            await interaction.response.send_message("⚠️ No permissions were selected.", ephemeral=True, delete_after=8)
        else:
            self.final_result = self.temp_result.copy()
            await self.prev_followup.delete()
            await interaction.response.defer(ephemeral=True)
            await interaction.delete_original_response()
            self.stop()


class Roles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.create_group = bot.tree.get_command('create')
        self.role_group = bot.tree.get_command('role')
        self.add_role_commands()

    def add_role_commands(self):

        @self.create_group.command(
            name="role", 
            description="Create a role.")
        @app_commands.describe(
            role_name="The name of the role you want to create.",
            color_hex="The hex color code for the role (e.g. #FF5733).",
            hoist="Whether the role should be displayed separately in the online members list.",
            mentionable="Whether this role can be mentioned by users.")
        async def create_role(interaction: discord.Interaction, role_name: str, color_hex: str, hoist: bool, mentionable: bool):          
            view = RoleCreationView(interaction)
            await interaction.response.send_message("☑️ Please select permissions for the role:", view=view, ephemeral=True)
            await view.wait()

            if not view.final_result:
                return

            permissions = Permissions.none()
            for perm in view.final_result:
                setattr(permissions, perm, True)

            try:
                color = discord.Color(int(color_hex.lstrip('#'), 16))
            except ValueError:
                await interaction.followup.send("❌ Invalid hex color code. Please provide a valid hex code like '#FF5733'.", ephemeral=True)
                return

            guild = interaction.guild
            role = await guild.create_role(
                name=role_name,
                permissions=permissions,
                color=color,
                hoist=hoist,
                mentionable=mentionable)

            await interaction.followup.send(
                f"🥳 Role `{role_name}` created. 🥳\n\n"
                f"**ADDED PERMISSIONS:**\n" + '\n'.join([f"✅ {perm}" for perm in view.final_result]),
                ephemeral=True)


        @self.role_group.command(
                name="assign",
                description="Assign multiple roles to a user.")
        @app_commands.describe(
            user="The user you want to assign roles to.")
        async def assign_role(interaction: discord.Interaction, user: discord.Member):
            guild_roles = interaction.guild.roles[1:]  # Exclude @everyone role
            user_roles = user.roles

            assignable_roles = [role for role in guild_roles if role not in user_roles]

            if not assignable_roles:
                await interaction.response.send_message(f"❌ {user.mention} already has all the assignable roles.", ephemeral=True)
                return

            options = [SelectOption(label=role.name, value=str(role.id)) for role in assignable_roles]

            select = discord.ui.Select(
                placeholder="Select roles to assign",
                options=options,
                min_values=1,
                max_values=len(assignable_roles),
                custom_id="role_assign_select")

            async def select_callback(interaction: discord.Interaction):
                if interaction.response.is_done():
                    await interaction.followup.defer(ephemeral=True)
                else:
                    await interaction.response.defer(ephemeral=True)

                selected_role_ids = [int(role_id) for role_id in select.values]
                roles_to_assign = [discord.utils.get(assignable_roles, id=role_id) for role_id in selected_role_ids]
                can_assign = []
                unassignable = []

                for role in roles_to_assign:
                    try:
                        await user.add_roles(role)
                        can_assign.append(role)
                    except discord.Forbidden:
                        unassignable.append(role)

                message = ""

                if can_assign:
                    assigned_roles = '\n'.join([f"✅ Assigned role: `{role.name}`" for role in can_assign])
                    message += f"**Assigned Roles:**\n{assigned_roles}\n\n"

                if unassignable:
                    unassignable_roles = '\n'.join([f"❌ Could not assign role: `{role.name}`" for role in unassignable])
                    message += f"**Unassignable Roles:**\n{unassignable_roles}"

                if message:
                    await interaction.followup.send(message, ephemeral=True)
                else:
                    await interaction.followup.send("No roles were assigned or failed to assign.", ephemeral=True)

                await interaction.delete_original_response()

            select.callback = select_callback

            view = discord.ui.View()
            view.add_item(select)
            await interaction.response.send_message(f"⚙️ Select roles to assign to {user.mention}:", view=view, ephemeral=True)

        @self.role_group.command(
            name="unassign",
            description="Unassign multiple roles from a user.")
        @app_commands.describe(
            user="The user you want to unassign roles from.")
        async def unassign_role(interaction: discord.Interaction, user: discord.Member):
            user_roles = user.roles[1:]
            
            if not user_roles:
                await interaction.response.send_message(f"❌ {user.mention} has no unassignable roles.", ephemeral=True)
                return
           
            options = [SelectOption(label=role.name, value=str(role.id)) for role in user_roles]           
            select = discord.ui.Select(
                placeholder="Select roles to unassign",
                options=options,
                min_values=1,
                max_values=len(user_roles),
                custom_id="role_unassign_select")
            
            async def select_callback(interaction: discord.Interaction):
                if interaction.response.is_done():
                    await interaction.followup.defer(ephemeral=True)
                else:
                    await interaction.response.defer(ephemeral=True)

                selected_role_ids = [int(role_id) for role_id in select.values]
                roles_to_unassign = [discord.utils.get(user_roles, id=role_id) for role_id in selected_role_ids]
                can_remove = []
                unremovable = []

                for role in roles_to_unassign:
                    try:
                        await user.remove_roles(role)
                        can_remove.append(role)
                    except discord.Forbidden:
                        unremovable.append(role)

                message = ""

                if can_remove:
                    removed_roles = '\n'.join([f"✅ Removed role: `{role.name}`" for role in can_remove])
                    message += f"**Removed Roles:**\n{removed_roles}\n\n"

                if unremovable:
                    unremovable_roles = '\n'.join([f"❌ Could not remove role: `{role.name}`" for role in unremovable])
                    message += f"**Unremovable Roles:**\n{unremovable_roles}"

                if message:
                    await interaction.followup.send(message, ephemeral=True)
                else:
                    await interaction.followup.send("No roles were removed or failed to remove.", ephemeral=True)

                await interaction.delete_original_response()

            select.callback = select_callback

            view = discord.ui.View()
            view.add_item(select)
            await interaction.response.send_message(f"⚙️ Select roles to unassign from {user.mention}:", view=view, ephemeral=True)


        @self.role_group.command(
            name="edit",
            description="Edit the permissions and properties of an existing role.")
        @app_commands.describe(
            role="The role you want to edit.",
            name="New name for the role.",
            color="Hex color code for the role.",
            hoist="Whether to display role separately.",
            mentionable="Whether the role can be mentioned.")
        async def edit_role(interaction: discord.Interaction, role: discord.Role, name: str = None, color: str = None, hoist: bool = None, mentionable: bool = None):

            view = RoleEditView(interaction, role)
            await interaction.response.send_message(
                f"📝 Editing role `{role.name}`. Please update the permissions (if needed):", 
                view=view, 
                ephemeral=True)

            await view.wait()

            # Update permissions only if the user modified them
            permissions = role.permissions
            if view.final_result:
                for perm in PERMISSIONS_LIST:
                    setattr(permissions, perm, perm in view.final_result)
                await role.edit(permissions=permissions)

            # Optionals
            updated_properties = []
            if name:
                await role.edit(name=name)
                updated_properties.append(f"Name: `{name}`")
            if color:
                try:
                    color_obj = discord.Color(int(color.lstrip('#'), 16))
                    await role.edit(color=color_obj)
                    updated_properties.append(f"Color: `{color}`")
                except ValueError:
                    await interaction.followup.send("❌ Invalid hex color code provided.", ephemeral=True)
                    return
            if hoist is not None:
                await role.edit(hoist=hoist)
                updated_properties.append(f"Hoist: `{hoist}`")
            if mentionable is not None:
                await role.edit(mentionable=mentionable)
                updated_properties.append(f"Mentionable: `{mentionable}`")

            await interaction.followup.send(
                f"✅ Role `{role.name}` has been updated with the following properties:\n" +
                "\n".join(updated_properties),
                ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Roles(bot))



