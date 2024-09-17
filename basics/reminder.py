import discord
from discord import app_commands 
from discord.ui import TextInput, Modal, Select, View
from datetime import datetime, timedelta
import asyncio
from discord.ui import Button, View



class ReminderEmbed(): #Customised Reminder
    """
    Make customised reminder embed
    """
    def __init__(self, date, time, msg):
        self.date= date
        self.time= time
        self.msg= msg

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


async def setCustomReminder(date_str, time_str, message, destination):
    #Since this is an async functn, It runs seperately for every call of setCustomReminder (thereby able to set multiple reminders at the same time). 
    #Each call awaits defined time executes seperately
    try:
       
        reminder_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M") # Combine date and time into a single datetime object
        current_time = datetime.now()
        
        delay = (reminder_datetime - current_time).total_seconds() #delay
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

        current_date= datetime.date(datetime.now())
        if entered_date == current_date: #if today date        
            current_time= datetime.time(datetime.now())# Check entered time more then current time
            if entered_time < current_time :
                return "Time already passed" 
        
        if entered_date < current_date: #Past date
            return "Date has already passed"
        
        return True


class ChannelSelectView(View): # View class with Select dropdown for channel selection
    def __init__(self, date, time, message, guild, modal_on_submit_interaction: discord.Interaction):
        super().__init__()
        #Need these data cuz validation is done on callback of this class
        self.date = date
        self.time = time
        self.message = message
        self.prev_interaction= modal_on_submit_interaction

        
        self.channel_select = Select( #Dropdown Channel Select
            placeholder="Choose a channel...",
            min_values=1,
            max_values=1,
            options=[]  #Select options
        )

        # populate the dropdown with channel names as options
        self.channel_select.add_option(label="None (DM)", value="DM")
        for channel in guild.text_channels:
            self.channel_select.add_option(label=channel.name, value=str(channel.id))
    
        self.channel_select.callback = self.channel_select_callback   #set callback function    
        self.add_item(self.channel_select) #add to view


    async def channel_select_callback(self, interaction: discord.Interaction): #Callback on channel select    
        # channel ID or None("DM")
        selected_option= self.channel_select.values[0]  #False if DM, else an ID 
        selected_channel= None
        if selected_option != "DM":
            selected_channel = interaction.guild.get_channel(int(selected_option))

        await self.prev_interaction.delete_original_response()
        
        if selected_channel is not None: #When Channel selected
            await interaction.response.send_message(f"Reminder set successfully in {selected_channel.mention}!", ephemeral=True, delete_after=15)                  
            await setCustomReminder(self.date ,self.time ,self.message , selected_channel) #SET REMINDERS FOR CHANNELS

        else:                           #No channel selected- i.e DM
            await interaction.response.send_message(f"Reminder set successfully in your dm! {interaction.user.mention}", ephemeral=True ,delete_after=15)          
            await setCustomReminder(self.date ,self.time ,self.message , interaction.user) #SET REMINDERS FOR USER DM          
        
           
class RestartButtonView(View):
    def __init__(self, error, on_submit_interaction: discord.Interaction, date, time, message):
            super().__init__(timeout=None)  # No timeout for this view
            self.error= error
            self.interaction= on_submit_interaction
            self.prev_date = date 
            self.prev_time= time
            self.prev_message= message

    @discord.ui.button(label="Try Again", style=discord.ButtonStyle.primary, custom_id="restart_button")
    async def restart_button_callback(self, interaction: discord.Interaction, button: Button):
       
        await self.interaction.delete_original_response()  #Delete reminder modal on_submit() interaction response
 
        update_modal= ReminderModel(title= str(self.error)) #Re-fill/Re-enter modal
        #Populate with previously entered data
        update_modal.date_input.default= self.prev_date
        update_modal.time_input.default= self.prev_time
        update_modal.message_input.default= self.prev_message

        await interaction.response.send_modal(update_modal) #Send update modal 


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
        date = self.date_input.value
        time = self.time_input.value
        message = self.message_input.value

        validation = TimeDateValidation(date= date, time= time)
        result= validation.validate() #Validation of entered date & time

        if result==True:#Validation PASSED       
            view = ChannelSelectView(date, time, message, interaction.guild, interaction) #Channel select dropdown instance
            await interaction.response.send_message("Select a channel to send the reminder:", view=view, ephemeral=True)

        else:#Validation FAILED
            restart_view= RestartButtonView(f" ❌ {result} ❌ ", interaction, date, time, message) #Restart process button
            await interaction.response.send_message(f"__**Error**__: ***{result}***", view= restart_view, ephemeral=True)          


@app_commands.command(name="remind", description="Set a reminder for a channel or as a DM")
async def set_reminder(interaction: discord.Interaction):

    reminder_model= ReminderModel() #Startup modal with empty fields
    await interaction.response.send_modal(reminder_model)




#Set repeat reminder