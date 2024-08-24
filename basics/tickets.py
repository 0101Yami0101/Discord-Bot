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

        # Check if already exists for the user
        existing_thread = discord.utils.get(guild.threads, name=f'ticket-{author.name.lower()}')
        if existing_thread:
            await interaction.response.send_message(f'{author.mention}, you already have an open ticket: {existing_thread.mention}', ephemeral=True)
            return
        
        # Create new
        ticket_thread = await channel.create_thread(
            name=f'ticket-{author.name.lower()}',
            auto_archive_duration=1440,  
            invitable= False,
            slowmode_delay=0
        )

        await ticket_thread.add_user(author)#add user to thread
        await interaction.response.send_message(f'{author.mention}, Your Ticket Is Created -> {ticket_thread.mention} ', ephemeral=True) #ack

        
        embed = discord.Embed(title="Your Ticket", description=f"Click the button below to close or delete your ticket.", color=0xE74C3C)
        await ticket_thread.send(embed= embed)       
        await add_delete_and_close_button(thread= ticket_thread, author= author)
        

    #Delete ticket
    elif interaction.data["custom_id"] == "delete_ticket":
        author = interaction.user
        guild = interaction.guild
        channel = interaction.channel
        ticket_thread = discord.utils.get(guild.threads, id= channel.id )
        
        if ticket_thread:
            await ticket_thread.delete()

    #Close ticket
    elif interaction.data["custom_id"] == "close_ticket":
        author = interaction.user
        guild = interaction.guild
        channel = interaction.channel


        ticket_thread = discord.utils.get(guild.threads, id= channel.id )
        
        if ticket_thread:
            await interaction.response.send_message(f'{author.mention} closed this ticket. Bye!')
            await ticket_thread.edit(archived= True,locked= True)
        
        else:
            await channel.send(f'You can not close this channel!')


async def add_delete_and_close_button(thread, author):

    closeButton = Button(label="Close", style=discord.ButtonStyle.grey, custom_id="close_ticket")
    delButton = Button(label="Delete", style=discord.ButtonStyle.red, custom_id="delete_ticket")
    view = View()
    view.add_item(closeButton)
    view.add_item(delButton)
    await thread.send(view= view)
    await thread.send(author.mention)




# Helper/
# def print_enabled_permissions(permissions):
#   
#     all_permissions = [perm for perm in dir(permissions) if isinstance(getattr(permissions, perm), bool)]
#     enabled_permissions = [perm for perm in all_permissions if getattr(permissions, perm)]
    
#     print("Enabled permissions:")
#     for perm in enabled_permissions:
#         print(perm)