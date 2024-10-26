import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput
from datetime import datetime
import aiohttp
import asyncio
import pytz


class FrequencyDropdown(discord.ui.Select):
    def __init__(self, event_details, prev_interaction: discord.Interaction):
        self.event_details = event_details
        self.prev_interaction = prev_interaction
        today = datetime.now().strftime("%A")

        options = [
            discord.SelectOption(label="Does not repeat", value="no_repeat"),
            discord.SelectOption(label=f"Weekly on {today}", value="weekly"),
            discord.SelectOption(label=f"Every other {today}", value="biweekly"),
            discord.SelectOption(label=f"Monthly on the second {today}", value="monthly"),
            discord.SelectOption(label="Annually on this date", value="annually"),
            discord.SelectOption(label="Every weekday", value="weekday")
        ]

        super().__init__(placeholder="Select event frequency...", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_frequency_label = [option.label for option in self.options if option.value == self.values[0]][0]
        self.event_details["frequency"] = selected_frequency_label
        await interaction.response.defer(ephemeral=True)
        await self.prev_interaction.delete_original_response()

        upload_image_msg= await interaction.followup.send(
            content=f"⚠️ Discord API doesn't currently support setting custom frequency. So default will be applied after selecting any other option.⚠️"
                    f"\n🖼️ Now, please upload an image, provide a URL, or type 'skip' to not add any image.",
            ephemeral=True
        )

        # Get IMAGE or URL
        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            msg = await interaction.client.wait_for("message", check=check, timeout=60)

            if msg.attachments:
                # If an attachment is sent
                self.event_details["image"] = msg.attachments[0].url
            elif msg.content.startswith("http") and self.is_valid_url(msg.content):
                # If a valid URL is sent
                self.event_details["image"] = msg.content
            elif msg.content.lower() == "skip":
                # If the message is "skip"
                self.event_details["image"] = None
            else:
                # Invalid input
                await interaction.followup.send(
                    content="❌ Invalid input. Please try again with a valid input'.",
                    ephemeral=True,
                )
                return
            
            guild = interaction.guild
            img_byte = await self.fetchImgBytes(self.event_details['image']) if self.event_details['image'] is not None else None

            #CREATE EVENT
            if 'channel_id' in self.event_details:
                channel = guild.get_channel(int(self.event_details['channel_id']))                             
                event_kwargs = {
                    "name": self.event_details['topic'],
                    "start_time": self.formatTime(self.event_details['start_date_time']),
                    "channel": channel,
                    "description": self.event_details['description'],
                    "privacy_level": discord.PrivacyLevel.guild_only,
                }
                if img_byte is not None:
                    event_kwargs["image"] = img_byte

                await guild.create_scheduled_event(**event_kwargs)

            elif 'location' in self.event_details: #EXTERNAL EVENT
                location = self.event_details['location']
                event_kwargs = {
                    "name": self.event_details['topic'],
                    "start_time": self.formatTime(self.event_details['start_date_time']),
                    "location": location,
                    "description": self.event_details['description'],
                    "privacy_level": discord.PrivacyLevel.guild_only,
                    "end_time": self.formatTime(self.event_details['end_date_time']),
                    "entity_type": discord.EntityType.external
                }
                if img_byte is not None:
                    event_kwargs["image"] = img_byte

                await guild.create_scheduled_event(**event_kwargs)

            else:
                await interaction.followup.send(
                    content=f"❌ Error occured while creating event. Please try again",
                    ephemeral=True
                )
                return
            
            await upload_image_msg.delete()
            await interaction.followup.send(
                    content=f"✅🥳  Created Event: **{self.event_details['topic']}** set to start on 📅: **{self.event_details['start_date_time']}** 🕑 🥳 ",
                    ephemeral=True
                )
            await msg.delete()

        except asyncio.TimeoutError:

            await interaction.followup.send("🛑 Image upload timed out. Please try again.", ephemeral=True)
        except Exception as e:

            error_message = str(e)
            specific_error = "Cannot schedule event in the past"
            if specific_error in error_message:
                await interaction.followup.send(f"❌ Error occurred: {specific_error}. Set a time in the future.", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Error occurred: 🚫{error_message}.", ephemeral=True)


    async def fetchImgBytes(self, img_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(img_url) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    raise ValueError("❌ Failed to fetch the image.")

    def formatTime(self, date_time_str):
        naive_start_time = datetime.strptime(f"{date_time_str}", "%Y-%m-%d %H:%M")
        timezone = pytz.timezone('Asia/Kolkata')
        aware_start_time = timezone.localize(naive_start_time)
        return aware_start_time

    def is_valid_url(self, url):
        import re
        regex = re.compile(
            r'^(https?|ftp)://[^\s/$.?#].[^\s]*$',
            re.IGNORECASE
        )
        return re.match(regex, url) is not None


class EventDetailsModal(Modal):
    def __init__(self, event_details):
        self.event_details = event_details
        super().__init__(title="Event Details")

        self.add_item(TextInput(
            label="Event Topic",
            placeholder="Enter the topic of the event...",

        ))
        self.add_item(TextInput(
            label="Start Date and Time(24h)",
            placeholder="YYYY-MM-DD HH:MM",
            style=discord.TextStyle.short,
        ))
        self.add_item(TextInput(
            label="Description",
            placeholder="Enter a description for the event...",
            style=discord.TextStyle.long,
            required=False,
            row=4
        ))

        if 'location' in self.event_details:
            self.add_item(TextInput(
                label="End Date and Time(24h)",
                placeholder="YYYY-MM-DD HH:MM",
                style=discord.TextStyle.short,
           
            ))

    async def on_submit(self, interaction: discord.Interaction):
        self.event_details["topic"] = self.children[0].value
        self.event_details["start_date_time"] = self.children[1].value
        self.event_details["description"] = self.children[2].value or "No description provided"
        if 'location' in self.event_details:
            self.event_details["end_date_time"] = self.children[3].value
            
        frequency_view = View()
        frequency_view.add_item(FrequencyDropdown(self.event_details, interaction))

        await interaction.response.send_message(
            content=f"🔁 Select a frequency for the event",
            view=frequency_view,
            ephemeral=True
        )


class NextStepButton(discord.ui.Button):
    def __init__(self, event_details, prev_interaction: discord.Interaction):
        super().__init__(label="Click To Proceed", style=discord.ButtonStyle.primary)
        self.event_details = event_details
        self.prev_interaction = prev_interaction

    async def callback(self, interaction: discord.Interaction):
        # Send the EventDetailsModal when the button is pressed
        modal = EventDetailsModal(self.event_details)
        await interaction.response.send_modal(modal)
        await self.prev_interaction.delete_original_response()


class NextStepView(discord.ui.View):
    def __init__(self, event_details, prev_interaction):
        super().__init__(timeout=None)
        self.event_details = event_details
        self.prev_interaction = prev_interaction
        self.add_item(NextStepButton(self.event_details, self.prev_interaction))


class CollectLocationUrl(Modal): #Other location
    def __init__(self, event_details):
        super().__init__(title="Enter Event Location URL")

        self.event_details= event_details
        self.add_item(TextInput(
            label="Event Location URL.",
            placeholder="Enter location (Text channel, external location)...",
            style=discord.TextStyle.short
        ))

    async def on_submit(self, interaction: discord.Interaction):

        self.event_details['location']= self.children[0].value
        view = NextStepView(self.event_details, interaction)
        await interaction.response.send_message(
            content=f"📍 Location received.",
            view=view,
            ephemeral=True
        )


class AvailableChannelsDropdown(discord.ui.Select): #Stage or #Voice
    def __init__(self, available_channels, event_details, prev_interaction: discord.Interaction):
        self.event_details = event_details
        self.prev_interaction = prev_interaction

        options = [
            discord.SelectOption(label=channel.name, value=str(channel.id))
            for channel in available_channels
        ]
        super().__init__(placeholder="Select a channel...", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_channel_id = self.values[0]
        self.event_details["channel_id"] = selected_channel_id
        modal = EventDetailsModal(self.event_details)
        await interaction.response.send_modal(modal)
        await self.prev_interaction.delete_original_response()


class ChannelTypeDropdown(discord.ui.Select):
    def __init__(self, cog, event_details, prev_interaction: discord.Interaction):
        self.cog = cog
        self.event_details = event_details
        self.prev_interaction= prev_interaction
        options = [
            discord.SelectOption(label="Stage", description="Select for a Stage Channel", value="stage"),
            discord.SelectOption(label="Voice", description="Select for a Voice Channel", value="voice"),
            discord.SelectOption(label="Somewhere else", description="Select for another type of channel or external location", value="other"),
        ]
        super().__init__(placeholder="Choose a channel type...", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0]
        await self.cog.handle_channel_selection(interaction, selected_value, self.event_details)
        await self.prev_interaction.delete_original_response()


class CreateEventsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.create_group = bot.tree.get_command('create')
        self.add_create_event_commands()

    def add_create_event_commands(self):
        @self.create_group.command(
            name="event",
            description="Create an Scheduled Event in any selected channel."
        )
        async def create_event(interaction: discord.Interaction):
            event_details = {}
            select_channel_view = View()
            select_channel_view.add_item(ChannelTypeDropdown(self, event_details, interaction))
            
            await interaction.response.send_message( #1
                "🏷️ Select a channel type to create an event.",
                view=select_channel_view,
                ephemeral=True
            )

    async def handle_channel_selection(self, interaction: discord.Interaction, selected_type: str, event_details):

        if selected_type == "voice":
            available_channels = [ch for ch in interaction.guild.voice_channels]
            channel_type = "Voice Channels"
            if available_channels:
                select_channel_view = View()
                select_channel_view.add_item(AvailableChannelsDropdown(available_channels, event_details, interaction))
                await interaction.response.send_message(
                    f"🔘 Please select from the available {channel_type}.",
                    view=select_channel_view,
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"🔴 No {channel_type} available. Try a different method",
                    ephemeral=True,
                    delete_after=30
                )

        elif selected_type == "stage":
            available_channels = [ch for ch in interaction.guild.stage_channels]
            channel_type = "Stage Channels"

            if available_channels:
                select_channel_view = View()
                select_channel_view.add_item(AvailableChannelsDropdown(available_channels, event_details, interaction))
                await interaction.response.send_message(
                    f"🔘 Please select from the available {channel_type}.",
                    view=select_channel_view,
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"🔴 No {channel_type} available. Try a different method",
                    ephemeral=True,
                    delete_after=30
                )

        elif selected_type == "other":
            location_modal= CollectLocationUrl(event_details)
            await interaction.response.send_modal(location_modal)
    

async def setup(bot: commands.Bot):
    await bot.add_cog(CreateEventsCog(bot))


