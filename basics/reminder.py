import discord
from discord import app_commands 
from discord.ui import TextInput, Modal, Select, View
from datetime import datetime, timedelta
import asyncio


channelselectoption= None
class ReminderEmbed():
    def __init__(self, date, time, msg):
        self.date= date
        self.time= time
        self.msg= msg

    def generate_embed(self):

        embed = discord.Embed(
            title="⏰REMINDER!",
            description=self.msg,
            color=discord.Color.blue()
        )
        embed.add_field(name="Date", value=self.date, inline=False)
        embed.add_field(name="Time", value=self.time, inline=False)
        embed.set_footer(text="Reminder created by your friendly bot!")
        embed.timestamp = discord.utils.utcnow()

        return embed




async def setCustomReminder(date_str, time_str, message, destination):
    #Since this is an async functn, It runs seperately for every call of setCustomReminder (thereby able to set multiple reminders at the same time). 
    #Each call awaits defined time executes seperately
    try:
        # Combine date and time into a single datetime object
        reminder_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        current_time = datetime.now()

        #delay
        delay = (reminder_datetime - current_time).total_seconds()
        await asyncio.sleep(delay)

        # Check if the destination is a channel or a user
        if isinstance(destination, discord.TextChannel):
            embed= ReminderEmbed(date_str, time_str, message).generate_embed()
            await destination.send(embed= embed)
        elif isinstance(destination, discord.Member):
            embed= ReminderEmbed(date_str, time_str, message).generate_embed()
            await destination.send(embed= embed)
        else:
            print("Invalid destination provided.")
    except ValueError as e:
        print(f"Error parsing date or time: {e}")
    except Exception as e:
        print(f"An error occurred while setting the reminder: {e}")


class TimeDateValidation():
    def __init__(self, date, time):
        self.date_entered= date
        self.time_entered= time

    def validate(self):
        try:
            entered_date = datetime.strptime(self.date_entered, "%Y-%m-%d").date()
        except ValueError:
            return "Invalid date. Enter YYYY-MM-DD format."
        try:
            entered_time = datetime.strptime(self.time_entered, "%H:%M").time()
        except ValueError:
            return "Invalid time. Enter HH:MM format."

        entered_datetime = datetime.combine(entered_date, entered_time)
        current_datetime = datetime.now()
        buffer_datetime = current_datetime + timedelta(seconds=10)
        # At least few sec + currtime
        if entered_datetime < buffer_datetime:
            return "Set a valid time in future."
        
        return True

# View class with Select dropdown for channel selection
class ChannelSelectView(View):
    def __init__(self, date, time, message, guild):
        super().__init__()
        #Need this data cuz validation is done on callback of this class
        self.date = date
        self.time = time
        self.message = message

        # Create a dropdown 
        self.channel_select = Select(
            placeholder="Choose a channel...",
            min_values=1,
            max_values=1,
            options=[]  # Initialize with an empty list
        )

        # Dynamically populate the dropdown with channel names as options
        self.channel_select.add_option(label="None (DM)", value="DM")
        for channel in guild.text_channels:
            self.channel_select.add_option(label=channel.name, value=str(channel.id))

        #set callback function
        self.channel_select.callback = self.channel_select_callback     
        self.add_item(self.channel_select) #add to view


    #callback functn
    async def channel_select_callback(self, interaction: discord.Interaction):
        global channelselectoption
        # selected channel ID or None("Dm")
        selected_option= self.channel_select.values[0]  #False if DM, else an ID 
        selected_channel= None
        if selected_option != "DM":
            selected_channel = interaction.guild.get_channel(int(selected_option))

        resp= await interaction.original_response()
        resp.delete(delay=2)
        
        #Validate Date Time
        validation = TimeDateValidation(self.date, self.time)
        result= validation.validate()

        if result is True: #passed validation
            if selected_channel is not None: #When Channel selected

                await interaction.response.send_message(f"Reminder set successfully in {selected_channel.mention}!", ephemeral=True, delete_after=15)
                #SET REMINDERS FOR CHANNELS            
                await setCustomReminder(self.date ,self.time ,self.message , selected_channel)

            else: #No channel selected- i.e DM
                await interaction.response.send_message(f"Reminder set successfully in your dm! {interaction.user.mention}", ephemeral=True ,delete_after=15)
                #SET REMINDERS FOR USER DM
                await setCustomReminder(self.date ,self.time ,self.message , interaction.user)           

        else: #Validation failed
            redo_modal= ReminderModel(title= f"Error- {validation.validate()}" )
            await interaction.response.send_modal(redo_modal)
           


#Modal
class ReminderModel(Modal):
    def __init__(self, title="⏰Add Reminder"):
        super().__init__(title= title)

        self.date_input = TextInput(label="Date (YYYY-MM-DD)", placeholder="Enter the date")
        self.time_input = TextInput(label="Time (HH:MM) (24hr)", placeholder="Enter the time")
        self.message_input = TextInput(label="Message", style=discord.TextStyle.long, placeholder="Enter your message")

        # Add to model
        self.add_item(self.date_input)
        self.add_item(self.time_input)
        self.add_item(self.message_input)
        

    async def on_submit(self, interaction: discord.Interaction):
        global channelselectoption
        date = self.date_input.value
        time = self.time_input.value
        message = self.message_input.value
       # Create dropdown menu 
        view = ChannelSelectView(date, time, message, interaction.guild) 
        await interaction.response.send_message("Select a channel to send the reminder:", view=view, ephemeral=True)
        



  
@app_commands.command(name="remind", description="Set a reminder for a channel or as a DM")
async def set_reminder(interaction: discord.Interaction):

    reminder_model= ReminderModel()
    await interaction.response.send_modal(reminder_model)