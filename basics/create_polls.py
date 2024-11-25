import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class PollCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_polls = {}  

    @app_commands.command(name="poll", description="Create a poll with a question and options.")
    async def poll(self, interaction: discord.Interaction):
        """Create a poll with a question and options."""
        await interaction.response.send_message("Please enter the poll question:", ephemeral=True)

        def check_message(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            question_msg = await self.bot.wait_for("message", timeout=60.0, check=check_message)
            question = question_msg.content


            await interaction.followup.send("Now enter the poll options separated by commas (e.g., option1, option2, option3):", ephemeral=True)
            options_msg = await self.bot.wait_for("message", timeout=60.0, check=check_message)
            options = [option.strip() for option in options_msg.content.split(",") if option.strip()]

            if len(options) < 2:
                await interaction.followup.send("You need at least two options to create a poll.", ephemeral=True)
                return
            if len(options) > 9:
                await interaction.followup.send("You can only have up to 9 options for the poll.", ephemeral=True)
                return

            embed = discord.Embed(
                title=question,
                description="\n".join([f"{chr(127462 + i)}: {option}" for i, option in enumerate(options)]),
                color=discord.Color.blue()
            )
            poll_message = await interaction.channel.send(embed=embed)

            # Add reactions 
            emoji_list = [chr(127462 + i) for i in range(len(options))]  # 🅰, 🅱, etc.
            for emoji in emoji_list:
                await poll_message.add_reaction(emoji)

            # Store 
            self.active_polls[poll_message.id] = {}

            await interaction.followup.send("React with the corresponding emojis to vote!", ephemeral=False)

        except asyncio.TimeoutError:
            await interaction.followup.send("You took too long to respond. Please try again.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """Ensure users can react to only one option."""
        if user.bot:
            return

        if reaction.message.id in self.active_polls:
            user_reactions = self.active_polls[reaction.message.id]

            if user.id in user_reactions:
                # Remove previous reaction
                prev_emoji = user_reactions[user.id]
                if prev_emoji != reaction.emoji:
                    for react in reaction.message.reactions:
                        if react.emoji == prev_emoji:
                            await react.remove(user)

            # Update user reaction
            user_reactions[user.id] = reaction.emoji

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.User):
        """Clean up user reaction tracking."""
        if reaction.message.id in self.active_polls and user.id in self.active_polls[reaction.message.id]:
            del self.active_polls[reaction.message.id][user.id]

async def setup(bot: commands.Bot):
    await bot.add_cog(PollCog(bot))
