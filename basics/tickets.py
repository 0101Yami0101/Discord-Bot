import discord
from discord.ext import commands
from discord.ui import Button, View

@commands.command(name="ticket")
@commands.has_permissions(administrator=True)
async def create_ticket_channel(ctx):
    embed = discord.Embed(title="Ticket Channel", description="Click the button below to open a ticket.", color=0x00ff00)

    button = Button(label="Open", style=discord.ButtonStyle.green, custom_id="open_ticket")
    view = View()
    view.add_item(button)

    await ctx.send(embed=embed, view=view)


async def on_ticket_button_interaction(interaction):

    #Open Ticket
    if interaction.data["custom_id"] == "open_ticket":
        author = interaction.user
        guild = interaction.guild
        channel = interaction.channel

        # Check if a ticket thread already exists
        existing_thread = discord.utils.get(guild.threads, name=f'ticket-{author.name.lower()}')
        if existing_thread:
            await interaction.response.send_message(f'{author.mention}, you already have an open ticket: {existing_thread.mention}', ephemeral=True)
            return
        
        # Create a new ticket thread
        ticket_thread = await channel.create_thread(
            name=f'ticket-{author.name.lower()}',
            auto_archive_duration=1440,  # Duration for auto archiving the thread (24 hours)
            invitable=False,  # Make the thread private
            slowmode_delay=0  # No slowmode
        )

       
        
        # await ticket_thread.edit(name="Banana"

        admin_role = discord.utils.get(interaction.guild.roles, name="Admin")
        if admin_role:
            
            admin_permissions = ticket_thread.permissions_for(admin_role)

            
            admin_permissions.send_tts_messages = True
            admin_permissions.mention_everyone = True
            admin_permissions.embed_links = True
            admin_permissions.attach_files = True
            admin_permissions.read_messages = True

           
        else:
            print("Admin role not found")

        await add_close_button(thread= ticket_thread, author= author)
        await interaction.response.send_message(f'{author.mention}, your ticket has been created: {ticket_thread.mention}', ephemeral=True) #ack


    #Close ticket
    elif interaction.data["custom_id"] == "close_ticket":
        author = interaction.user
        guild = interaction.guild
        channel = interaction.channel
        ticket_thread = discord.utils.get(guild.threads, name=f'ticket-{author.name.lower()}')
        
        if ticket_thread:
            await ticket_thread.delete()
            await interaction.response.send_message(f'Your ticket has been closed.', ephemeral=True) #ack
        else:
            await interaction.response.send_message(f'No open ticket found to close.', ephemeral=True) #ack





async def add_close_button(thread, author):
    embed = discord.Embed(title="Your Ticket", description="Click the button below to close your ticket.", color=0xE74C3C)
    button = Button(label="Close", style=discord.ButtonStyle.red, custom_id="close_ticket")
    view = View()
    view.add_item(button)
    await thread.send(f'{author.mention}, your ticket has been created! Please describe your issue.', embed= embed, view= view)

#Send delete thread button -> can be done by admin only ! delete thread