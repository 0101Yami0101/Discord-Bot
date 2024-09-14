import discord
import json
import os
from discord.ext import commands
from discord import app_commands
from enum import Enum

DATA_DIR = 'data/level_data'
DATA_FILE = os.path.join(DATA_DIR, 'user_data.json')

class LevelMode(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class LevelUpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_data = self.load_user_data()
        self.levelling_system = False 
        self.level_mode = LevelMode.MEDIUM 

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not self.levelling_system:
            return
        
        if message.author.bot:
            return

        user_id = str(message.author.id)
        guild_id = str(message.guild.id)

        if guild_id not in self.user_data:
            self.user_data[guild_id] = {}
        if user_id not in self.user_data[guild_id]:
            self.user_data[guild_id][user_id] = {
                "xp": 0,
                "level": 1
            }

        self.user_data[guild_id][user_id]["xp"] += 5  # Adjust the XP increment as needed
        current_xp = self.user_data[guild_id][user_id]["xp"]
        current_level = self.user_data[guild_id][user_id]["level"]

        # Threshold based on the current mode
        if self.level_mode == LevelMode.EASY:
            next_level_xp = current_level ** 1 * 100
        elif self.level_mode == LevelMode.MEDIUM:
            next_level_xp = current_level ** 2 * 100
        elif self.level_mode == LevelMode.HARD:
            next_level_xp = current_level ** 3 * 100

        if current_xp >= next_level_xp:
            self.user_data[guild_id][user_id]["level"] += 1
            new_level = self.user_data[guild_id][user_id]["level"]

            await message.channel.send(
                f"🎉 {message.author.mention} has leveled up to level {new_level}!"
            )

        self.save_user_data()

    def load_user_data(self):
        """Load user data from the JSON file."""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_user_data(self):
        """Save user data to the JSON file."""
        with open(DATA_FILE, 'w') as f:
            json.dump(self.user_data, f, indent=4)

    # Leveling Group 
    leveling_group = app_commands.Group(name="leveling", description="Leveling system commands")

    @leveling_group.command(name="toggle", description="Enable or disable the leveling system")
    @app_commands.checks.has_permissions(administrator=True)
    async def toggle_leveling(self, interaction: discord.Interaction):
        self.levelling_system = not self.levelling_system
        status = "enabled" if self.levelling_system else "disabled"
        await interaction.response.send_message(f"Leveling system has been {status}.", ephemeral=True)

    @leveling_group.command(name="reset", description="Clear the user data")
    @app_commands.checks.has_permissions(administrator=True)  
    async def reset_data(self, interaction: discord.Interaction):
        if len(self.user_data) == 0:
            await interaction.response.send_message("No user data available.", ephemeral=True)
            return
        self.user_data = {}  # Clear the in-memory user data
        self.save_user_data()  # Clear the user data in the JSON file
        await interaction.response.send_message("User data has been reset.", ephemeral=True)

    @leveling_group.command(name="mode", description="Set the leveling difficulty mode")
    @app_commands.describe(level_mode="Harder it is, longer it takes to level up.")
    @app_commands.choices(level_mode=[
        app_commands.Choice(name="Easy", value=LevelMode.EASY.value),
        app_commands.Choice(name="Medium", value=LevelMode.MEDIUM.value),
        app_commands.Choice(name="Hard", value=LevelMode.HARD.value)
    ])
    @app_commands.checks.has_permissions(administrator=True) 
    async def set_mode(self, interaction: discord.Interaction, level_mode: str):
        if not self.levelling_system:
            await interaction.response.send_message("Please initialize the leveling system first by using 'leveling toggle'", ephemeral=True)
            return
        self.level_mode = LevelMode(level_mode)
        await interaction.response.send_message(f"Leveling mode has been set to {self.level_mode.value}.", ephemeral=True)

    @leveling_group.command(name="levels", description="Get the levels of all users or a specific user")
    @app_commands.describe(username="The name of the user to look up")
    async def get_levels(self, interaction: discord.Interaction, username: str = None):
        guild_id = str(interaction.guild.id)

        if not self.levelling_system:
            await interaction.response.send_message("Please initialize the leveling system first by using 'leveling toggle'", ephemeral=True)
            return

        if username is None:
            if guild_id not in self.user_data or len(self.user_data[guild_id]) == 0:
                await interaction.response.send_message("No user data available.", ephemeral=True)
                return

            all_users = []
            for user_id, data in self.user_data[guild_id].items():
                member = interaction.guild.get_member(int(user_id))
                if member:
                    all_users.append(f"{member.display_name}: Level {data['level']}")

            await interaction.response.send_message("\n".join(all_users), ephemeral=True)
        else:
            # Find the specific user
            member = discord.utils.get(interaction.guild.members, name=username)
            if not member:
                await interaction.response.send_message(f"User '{username}' not found.", ephemeral=True)
                return

            user_id = str(member.id)
            if guild_id in self.user_data and user_id in self.user_data[guild_id]:
                user_level = self.user_data[guild_id][user_id]["level"]
                await interaction.response.send_message(f"{username} is at level {user_level}.", ephemeral=True)
            else:
                await interaction.response.send_message(f"No data found for user '{username}'.", ephemeral=True)

# Add cog to the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(LevelUpCog(bot))
    await bot.tree.sync()
