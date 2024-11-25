import discord
from discord import app_commands, ButtonStyle
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button
import asyncio

class ReactionRoleModal(Modal, title="Create Reaction Roles"):
    def __init__(self):
        super().__init__()
        self.stop_collecting_event = asyncio.Event()  
        self.pairs = {}

        self.title_input = TextInput(
            label="Reaction Roles Title",
            style=discord.TextStyle.short,
            placeholder="Enter the title for the embed...",
            max_length=250
        )
        self.description_input = TextInput(
            label="Reaction Roles Description",
            style=discord.TextStyle.long,
            placeholder="Enter the description for reaction roles..."
        )
        self.add_item(self.title_input)
        self.add_item(self.description_input)

    async def on_submit(self, interaction: discord.Interaction):
        self.title = self.title_input.value
        self.description = self.description_input.value
        await self.collect_reaction_roles(interaction)

    async def collect_reaction_roles(self, interaction: discord.Interaction):
        """Collects reaction-role pairs from the user."""
        view = View()
        finish_button = Button(style=ButtonStyle.success, label="Finish")

        async def finish_button_callback(finish_interaction: discord.Interaction):
            if not self.pairs:
                await finish_interaction.response.send_message(
                    "Please add at least one role-emoji pair before finishing.",
                    ephemeral=True
                )
                return

            await finish_interaction.response.defer(ephemeral=True)

            embed = discord.Embed(
                title=f"**{self.title}**",
                description=f"{self.description}\n\n" +
                            '\n'.join(f"React with {emoji} for {role.mention}" for emoji, role in self.pairs.items()),
                color=discord.Color.green()
            )
            embed.set_footer(text="React below to get your role!")
            message = await finish_interaction.channel.send(embed=embed)

            for emoji in self.pairs.keys():
                await message.add_reaction(emoji)

            cog = finish_interaction.client.get_cog("ReactionRolesCog")
            if cog:
                cog.reaction_role_message_id = message.id
                cog.reaction_role_pairs = self.pairs

            await finish_interaction.followup.send("Reaction roles setup complete!", ephemeral=True)
            self.stop_collecting_event.set()  #Stop collection loop
            view.stop() 

        finish_button.callback = finish_button_callback
        view.add_item(finish_button)

        await interaction.response.send_message(
            "Input role-emoji pairs as `@role emoji`. Click 'Finish' when done.",
            view=view,
            ephemeral=True
        )

        while not self.stop_collecting_event.is_set():
            if self.stop_collecting_event.is_set():
                return
            try:
                user_input = await interaction.client.wait_for(
                    "message",
                    check=lambda m: m.author == interaction.user and m.channel == interaction.channel,
                    timeout=120
                )

                content = user_input.content.strip().split()
                if len(content) == 2:
                    role_mention, emoji = content
                    role = discord.utils.get(interaction.guild.roles, mention=role_mention)

                    if role:
                        # Check if the bot can assign the role
                        guild = interaction.guild
                        bot_member = guild.me  # Bot's member object
                        if bot_member.top_role.position <= role.position:
                            await interaction.followup.send(
                                f"Bot cannot assign the role {role.name} because it is higher than or equal to the bot's top role. "
                                "Please update the role hierarchy or choose a different role.",
                                ephemeral=True
                            )
                            continue
                        if not guild.me.guild_permissions.manage_roles:
                            await interaction.followup.send(
                                "Bot does not have permission to manage roles. Please update the bot's permissions.",
                                ephemeral=True
                            )
                            continue

                        if role in self.pairs.values():
                            await interaction.followup.send(f"Role {role.mention} is already assigned!", ephemeral=True)
                        elif emoji in self.pairs:
                            await interaction.followup.send(f"Emoji {emoji} is already in use!", ephemeral=True)
                        else:
                            self.pairs[emoji] = role
                            await interaction.followup.send(f"Added: {role.mention} -> {emoji}", ephemeral=True)
                    else:
                        if not self.stop_collecting_event.is_set():
                            await interaction.followup.send("Invalid role mention. Try again.", ephemeral=True)
                else:
                    if not self.stop_collecting_event.is_set():
                        await interaction.followup.send("Format: `@role emoji`. Try again.", ephemeral=True)

            except asyncio.TimeoutError:
                if not self.stop_collecting_event.is_set():
                    await interaction.followup.send("Setup timed out. Reaction roles not saved.", ephemeral=True)
                    break
         
            await asyncio.sleep(0) 



class ReactionRolesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reaction_role_message_id = None
        self.reaction_role_pairs = {}

    reaction_roles_group = app_commands.Group(name="reaction", description="Reaction roles setup commands.")

    @reaction_roles_group.command(name="roles", description="Set up reaction roles in this channel.")
    async def reaction_roles(self, interaction: discord.Interaction):
        modal = ReactionRoleModal()
        await interaction.response.send_modal(modal)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or reaction.message.id != self.reaction_role_message_id:
            return

        role = self.reaction_role_pairs.get(str(reaction.emoji))
        if role:
            member = reaction.message.guild.get_member(user.id)
            if member:
                try:
                    await member.add_roles(role)
                except Exception as e:
                    print(f"Failed to assign role: {e}")

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user.bot or reaction.message.id != self.reaction_role_message_id:
            return

        role = self.reaction_role_pairs.get(str(reaction.emoji))
        if role:
            member = reaction.message.guild.get_member(user.id)
            if member:
                try:
                    await member.remove_roles(role)
                except Exception as e:
                    print(f"Failed to remove role: {e}")


async def setup(bot):
    await bot.add_cog(ReactionRolesCog(bot))

