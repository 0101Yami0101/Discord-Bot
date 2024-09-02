import discord
from discord import app_commands, ButtonStyle
from discord.ext import commands
from discord.ui import View, Button
import asyncio  # Make sure to import asyncio for timeout handling

class ReactionRoleModal(discord.ui.Modal, title="Create Reaction Roles"):
    def __init__(self):
        super().__init__()

        # Text input for title and description
        self.title_input = discord.ui.TextInput(
            label="Reaction Roles Title",
            style=discord.TextStyle.short,
            placeholder="Enter the title for the embed...",
            max_length=250
        )
        self.description_input = discord.ui.TextInput(
            label="Reaction Roles Description",
            style=discord.TextStyle.long,
            placeholder="Enter the description for reaction roles..."
        )
        self.add_item(self.title_input)
        self.add_item(self.description_input)

    async def on_submit(self, interaction: discord.Interaction):
        # Store the description
        self.title = self.title_input.value
        self.description = self.description_input.value
        await self.collect_reaction_roles(interaction)

    async def collect_reaction_roles(self, interaction: discord.Interaction):
        """Collects reaction role pairs from the user."""
        pairs = {}  # Dictionary to store all the role-emoji pairs
        stop_collecting = False  # Flag to determine when to stop collecting input

        # View with finish button
        view = View()
        finish_button = Button(style=ButtonStyle.success, label='Finish', custom_id='finish')
        view.add_item(finish_button)

        # Finish Button callback
        async def finish_button_callback(interaction: discord.Interaction):
            """Callback for when the finish button is clicked."""
            nonlocal stop_collecting
            stop_collecting = True 

            embed = discord.Embed(
                title=self.title,
                description=self.description + '\n' + '\n'.join(f"{emoji} {role}" for emoji, role in pairs.items()),
                color=discord.Color.green()
            )

            await interaction.response.send_message("Generating..", ephemeral=True)

            # Send the embed and store the message to access it later
            embedded_msg = await interaction.channel.send(embed=embed)
            
            # Add reactions to the embed
            for emoji in pairs.keys():
                await embedded_msg.add_reaction(emoji)

            await interaction.delete_original_response()
            view.stop()

            # Store the message ID and the pairs for later role assignment
            interaction.client.reaction_role_message_id = embedded_msg.id
            interaction.client.reaction_role_pairs = pairs

        # Assign callback
        finish_button.callback = finish_button_callback

        await interaction.response.send_message(
            "Please input the emoji and role in the format: `@role emoji` (one pair per message). Example:\n@Member 😀\nClick 'Finish' when done.",
            view=view,
            ephemeral=True
        )

        while not stop_collecting:
            try:
                # Wait for the user's message or button click
                user_input = await interaction.client.wait_for(
                    'message',
                    check=lambda m: m.author == interaction.user and m.channel == interaction.channel,
                    timeout=120
                )
                
                # Split user input into role and emoji parts
                content = user_input.content.strip().split()
                if len(content) == 2:
                    role_mention, emoji = content
                    role = discord.utils.get(interaction.guild.roles, mention=role_mention)

                    if role:
                        if not stop_collecting:
                            pairs[emoji] = role
                            await interaction.followup.send(f"Added: {role_mention} with {emoji}", ephemeral=True)
                    else:
                        await interaction.followup.send("Invalid role mention. Please try again.", ephemeral=True)
                else:
                    await interaction.followup.send("Please provide input in the format `@role emoji`.", ephemeral=True)

            except asyncio.TimeoutError:
                if not stop_collecting:
                    await interaction.followup.send("Time out! No input received. Please try again.", ephemeral=True)
                    stop_collecting = True
                    view.stop()
                break


@app_commands.command(name="reaction_roles", description="Set reaction roles on this channel")
async def reaction(interaction: discord.Interaction):
    role_modal = ReactionRoleModal()  # Startup modal with empty fields
    await interaction.response.send_modal(role_modal)

# CREATE EVENT LISTENER TO ASSIGN ROLES TO USERS THAT REACT
#############################################################

