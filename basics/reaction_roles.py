import discord
from discord import app_commands, ButtonStyle
from discord.ext import commands
from discord.ui import View, Button
import asyncio

class ReactionRoleModal(discord.ui.Modal, title="Create Reaction Roles"):
    def __init__(self):
        super().__init__()
        self.header_interaction= None

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
        stop_collecting = False  # Flag to stop collecting input

        # View with finish button
        view = View()
        finish_button = Button(style=ButtonStyle.success, label='Finish', custom_id='finish')
        view.add_item(finish_button)
        self.header_interaction= interaction


        # Finish Button callback
        # Finish Button callback
        async def finish_button_callback(interaction: discord.Interaction):
            """Callback for when the finish button is clicked."""
            nonlocal stop_collecting
            nonlocal view

            if not pairs:
                await interaction.response.send_message("Please add at least one role-emoji pair before finishing.", ephemeral=True)
                return
            
            stop_collecting = True 
            embed = discord.Embed(
                title=f"**{self.title}**",  # Bold the title
                description=f"{self.description}\n\n" + '\n'.join(f"React with {emoji} for {role.mention} role" for emoji, role in pairs.items()),
                color=discord.Color.green()  # Custom color for the embed
            )
            embed.set_footer(text="Choose your role by reacting!", icon_url="https://cdn-icons-png.flaticon.com/512/5151/5151146.png")

            await interaction.response.send_message("Generating..", ephemeral=True)

            # Send the embed and store the message to access it later
            embedded_msg = await interaction.channel.send(embed=embed)                   
            for emoji in pairs.keys():  # Add reactions to the embed
                await embedded_msg.add_reaction(emoji)

          
            await interaction.delete_original_response()
            await self.header_interaction.delete_original_response()

            view.stop()  # Stop the view to prevent further interactions

            # Store the message ID and the pairs for later role assignment
            interaction.client.reaction_role_message_id = embedded_msg.id
            interaction.client.reaction_role_pairs = pairs

        # Assign callback
        finish_button.callback = finish_button_callback

        await interaction.response.send_message(
            "Please input the role and emoji in the format: `@role emoji` (one pair per message). Example:\n@Member 😀\nClick 'Finish' when done.",
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
                        # Check if bot has 'manage_roles' permission
                        bot_member = interaction.guild.get_member(interaction.client.user.id)
                        if not bot_member.guild_permissions.manage_roles:
                            await interaction.followup.send("I don't have permission to manage roles.", ephemeral=True)
                            continue

                        # Check if the bot's top role is higher than the target role
                        bot_top_role = bot_member.top_role
                        if bot_top_role <= role:
                            if not stop_collecting:
                                await interaction.followup.send(
                                    f"I can't assign the role {role_mention} because it is higher or equal to my highest role.",
                                    ephemeral=True
                                )
                                await user_input.delete()
                                continue

                        # Check if the role is already assigned to an emoji 
                        if role in pairs.values():
                            # Reassign the role to the new emoji
                            old_emoji = [key for key, val in pairs.items() if val == role][0]
                            pairs.pop(old_emoji)  # Remove the old emoji assignment
                            pairs[emoji] = role  # Add the new emoji assignment
                            await interaction.followup.send(f"Updated: {role_mention} to new emoji {emoji}.", ephemeral=True)
                            await user_input.delete()

                        # Check if the emoji is already assigned to another role
                        elif emoji in pairs.keys():
                            await interaction.followup.send(f"The emoji {emoji} is already assigned to another role. Please choose a different emoji.", ephemeral=True)
                            await user_input.delete()
                        
                        # Add the role-emoji pair if checks pass
                        else:
                            if not stop_collecting:
                                pairs[emoji] = role
                                await user_input.delete()
                                await interaction.followup.send(f"Added: {role_mention} with {emoji}", ephemeral=True, )
                                
                            
                    else:
                        await user_input.delete()
                        await interaction.followup.send("Invalid role mention. Please try again.", ephemeral=True)
                else:
                    await user_input.delete()
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


#Cog for Reaction Roles
class ReactionRolesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        #role pairs and embed msg id
        self.bot.reaction_role_message_id = None
        self.bot.reaction_role_pairs = {}

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user: discord.User):
        if user.bot:
            return  
        
        # Check if the reaction is on the correct message
        if reaction.message.id == self.bot.reaction_role_message_id:
            # Get the role associated with  emoji
            role = self.bot.reaction_role_pairs.get(str(reaction.emoji))           
            # Ensure the role exists
            if role:
                # Get the member object for the user
                guild = reaction.message.guild
                member = guild.get_member(user.id)
                if member:
                    try:
                        # Assign role 
                        await member.add_roles(role)
                    except Exception as e:
                        print(f"Unassignable {e}")

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user: discord.User):
        if user.bot:
            return

        if reaction.message.id == self.bot.reaction_role_message_id:
            role = self.bot.reaction_role_pairs.get(str(reaction.emoji))

            if role:
                guild = reaction.message.guild
                member = guild.get_member(user.id)
                if member:
                    try:
                        # Remove role
                        await member.remove_roles(role)
                    except Exception as e:
                        print(f"Unable to remove role: {e}")
         

    
#Cog setup
async def setup(bot):
    await bot.add_cog(ReactionRolesCog(bot))