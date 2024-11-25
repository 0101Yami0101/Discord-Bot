import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import TextInput, Modal, Select, View, Button
from datetime import datetime
import asyncio

class ReminderEmbed:
    """
    Create a customized reminder embed.
    """
    def __init__(self, date, time, msg):
        self.date = date
        self.time = time
        self.msg = msg

    def generate_embed(self):
        embed = discord.Embed(
            title="⏰REMINDER!⏰",
            description=self.msg,
            color=discord.Color.blue()
        )
        embed.add_field(name="Date", value=self.date, inline=False)
        embed.add_field(name="Time", value=self.time, inline=False)
        embed.set_footer(text="Reminder created by your friendly bot!")
        embed.timestamp = discord.utils.utcnow()
        return embed


async def set_custom_reminder(date_str, time_str, message, destination):
    """
    Asynchronous function to set reminders for a specific time and message.
    """
    try:
        reminder_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        current_time = datetime.now()
        delay = (reminder_datetime - current_time).total_seconds()
        await asyncio.sleep(delay)

        embed = ReminderEmbed(date_str, time_str, message).generate_embed()
        if isinstance(destination, discord.TextChannel):
            await destination.send(embed=embed)
        elif isinstance(destination, discord.Member):
            await destination.send(embed=embed)
    except Exception as e:
        print(f"Error setting reminder: {e}")


class TimeDateValidation:
    """
    Validate the date and time entered by the user.
    """
    def __init__(self, date, time):
        self.date = date
        self.time = time

    def validate(self):
        try:
            entered_date = datetime.strptime(self.date, "%Y-%m-%d").date()
            entered_time = datetime.strptime(self.time, "%H:%M").time()
        except ValueError:
            return "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM (24hr) for time."

        current_date = datetime.now().date()
        current_time = datetime.now().time()

        if entered_date < current_date:
            return "Date has already passed."
        if entered_date == current_date and entered_time <= current_time:
            return "Time has already passed."
        return True


class ReminderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class ReminderModal(Modal):
        def __init__(self, cog, title="⏰ Add Reminder"):
            super().__init__(title=title)
            self.cog = cog

            self.date_input = TextInput(label="Date (YYYY-MM-DD)", placeholder="Enter the date")
            self.time_input = TextInput(label="Time (HH:MM) (24hr)", placeholder="Enter the time")
            self.message_input = TextInput(label="Message", style=discord.TextStyle.long, placeholder="Enter your message")
            self.add_item(self.date_input)
            self.add_item(self.time_input)
            self.add_item(self.message_input)

        async def on_submit(self, interaction: discord.Interaction):
            date = self.date_input.value
            time = self.time_input.value
            message = self.message_input.value

            validation = TimeDateValidation(date, time)
            validation_result = validation.validate()

            if validation_result == True:
                view = self.cog.ChannelSelectView(date, time, message, interaction.guild, interaction)
                await interaction.response.send_message("Select a channel to send the reminder:", view=view, ephemeral=True)
            else:
                restart_view = self.cog.RestartButtonView(validation_result, interaction, date, time, message)
                await interaction.response.send_message(f"__**Error**__: {validation_result}", view=restart_view, ephemeral=True)

    class ChannelSelectView(View):
        def __init__(self, date, time, message, guild, modal_interaction: discord.Interaction):
            super().__init__()
            self.date = date
            self.time = time
            self.message = message
            self.modal_interaction = modal_interaction

            self.channel_select = Select(
                placeholder="Choose a channel...",
                options=[discord.SelectOption(label="DM", value="DM")] +
                        [discord.SelectOption(label=channel.name, value=str(channel.id)) for channel in guild.text_channels]
            )
            self.channel_select.callback = self.channel_select_callback
            self.add_item(self.channel_select)

        async def channel_select_callback(self, interaction: discord.Interaction):
            selected_option = self.channel_select.values[0]
            if selected_option == "DM":
                destination = interaction.user
            else:
                destination = interaction.guild.get_channel(int(selected_option))

            await self.modal_interaction.delete_original_response()
            await interaction.response.send_message(
                f"Reminder set successfully for {destination.mention if isinstance(destination, discord.TextChannel) else 'DM'}!",
                ephemeral=True
            )
            await set_custom_reminder(self.date, self.time, self.message, destination)

    class RestartButtonView(View):
        def __init__(self, error, interaction: discord.Interaction, date, time, message):
            super().__init__()
            self.error = error
            self.interaction = interaction
            self.date = date
            self.time = time
            self.message = message

            button = Button(label="Try Again", style=discord.ButtonStyle.primary)
            button.callback = self.restart
            self.add_item(button)

        async def restart(self, interaction: discord.Interaction):
            await self.interaction.delete_original_response()
            modal = ReminderCog.ReminderModal(self)
            modal.date_input.default = self.date
            modal.time_input.default = self.time
            modal.message_input.default = self.message
            await interaction.response.send_modal(modal)

    @app_commands.command(name="remind", description="Set a reminder for a channel or as a DM.")
    async def set_reminder(self, interaction: discord.Interaction):
        modal = self.ReminderModal(self)
        await interaction.response.send_modal(modal)


async def setup(bot: commands.Bot):
    await bot.add_cog(ReminderCog(bot))
