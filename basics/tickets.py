import discord
from discord.ext import commands
from discord.ui import Button, View


class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="ticket", description="Make the current channel a ticket channel for user support.")
    @discord.app_commands.default_permissions(administrator=True)
    async def create_ticket_channel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Ticket Channel",
            description="Click the button below to open a ticket.",
            color=discord.Color.green(),
        )
        button = Button(label="Open", style=discord.ButtonStyle.green, custom_id="open_ticket")
        view = View()
        view.add_item(button)

        await interaction.response.send_message(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.data.get("custom_id"):
            return
        if interaction.data["custom_id"] == "open_ticket":
            await self.handle_open_ticket(interaction)
        elif interaction.data["custom_id"] == "delete_ticket":
            await self.handle_delete_ticket(interaction)
        elif interaction.data["custom_id"] == "close_ticket":
            await self.handle_close_ticket(interaction)

    async def handle_open_ticket(self, interaction: discord.Interaction):
        author = interaction.user
        guild = interaction.guild
        channel = interaction.channel
        existing_thread = discord.utils.get(guild.threads, name=f"ticket-{author.name.lower()}")
        if existing_thread:
            await interaction.response.send_message(
                f"{author.mention}, you already have an open ticket: {existing_thread.mention}",
                ephemeral=True,
            )
            return
        ticket_thread = await channel.create_thread(
            name=f"ticket-{author.name.lower()}",
            auto_archive_duration=1440,
            invitable=False,
            slowmode_delay=0,
        )
        await ticket_thread.add_user(author)
        await interaction.response.send_message(
            f"{author.mention}, your ticket has been created: {ticket_thread.mention}",
            ephemeral=True,
        )
        embed = discord.Embed(
            title="Your Ticket",
            description="Click the buttons below to close or delete your ticket.",
            color=discord.Color.red(),
        )
        await ticket_thread.send(embed=embed)
        await self.add_ticket_controls(ticket_thread, author)

    async def handle_delete_ticket(self, interaction: discord.Interaction):
        channel = interaction.channel
        if isinstance(channel, discord.Thread):
            await channel.delete()
        else:
            await interaction.response.send_message("This is not a ticket thread!", ephemeral=True)

    async def handle_close_ticket(self, interaction: discord.Interaction):
        channel = interaction.channel
        if isinstance(channel, discord.Thread):
            await channel.edit(archived=True, locked=True)
            await interaction.response.send_message(
                f"{interaction.user.mention} closed this ticket. Goodbye!",
                ephemeral=False,
            )
        else:
            await interaction.response.send_message("This is not a ticket thread!", ephemeral=True)

    async def add_ticket_controls(self, thread: discord.Thread, author: discord.Member):
        close_button = Button(label="Close", style=discord.ButtonStyle.grey, custom_id="close_ticket")
        delete_button = Button(label="Delete", style=discord.ButtonStyle.red, custom_id="delete_ticket")
        view = View()
        view.add_item(close_button)
        view.add_item(delete_button)
        await thread.send(content=f"{author.mention}", view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(TicketCog(bot))
