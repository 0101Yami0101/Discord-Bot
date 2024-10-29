import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio

class RaffleBasic(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.raffle_group = bot.tree.get_command('raffle') 
        self.add_raffle_basic()
        self.add_raffle_embed()

    def add_raffle_basic(self):
        @self.raffle_group.command(
            name="basic", 
            description="Start a basic raffle.")
        @app_commands.describe(
            members="Enter the list of members (comma-separated by ID or mention)",
            winners="Number of winners to pick",
            timer="Time in seconds before raffle starts")
        async def basic_raffle(interaction: discord.Interaction, members: str, winners: int, timer: int):
            # Split the member 
            member_ids = [m.strip() for m in members.split(',') if m.strip()]
            
            # Actual discord.Member objects
            member_list = []
            for member_id in member_ids:
                member_id = member_id.replace("<@!", "").replace("<@", "").replace(">", "")
               
                try:
                    member = await interaction.guild.fetch_member(int(member_id))
                    if member: 
                        member_list.append(member.display_name)
                except (ValueError, discord.NotFound): #Skip invalid
                    continue

            if len(member_list) < winners: 
                await interaction.response.send_message(
                    f"❌ Not enough members for the number of winners!", ephemeral=True
                )
                return

            await interaction.response.send_message(
                f"🎟️ Raffle will start in {timer} seconds with {len(member_list)} members. Picking {winners} winners...", 
                ephemeral=False
            )

            await asyncio.sleep(timer)
            winning_members = random.sample(member_list, winners)
            
            embed = discord.Embed(
                title="🎉 Raffle Winners 🎉",
                description=f"Here are the lucky {winners} winner(s):",
                color=discord.Color.green()
            )
            for index, winner in enumerate(winning_members, start=1):
                embed.add_field(name=f"Winner #{index}", value=f"🏆 {winner}", inline=False)
            
            await interaction.followup.send(embed=embed)

    def add_raffle_embed(self):
        @self.raffle_group.command(
            name="embed", 
            description="Start an advanced raffle with a reaction-based entry.")
        @app_commands.describe(
            winners="Number of winners to pick",
            timer="Time in seconds before raffle ends")
        async def embed_raffle(interaction: discord.Interaction, winners: int, timer: int):

            embed = discord.Embed(
                title="🎉 Join the Raffle! 🎉",
                description=(
                    "React with 🎟️ to participate!\n"
                    f"The raffle will run for {timer} seconds, selecting **{winners} winner(s)**."
                ),
                color=discord.Color.purple()
            )
            message = await interaction.response.send_message(embed=embed)
            message = await interaction.original_response()
            
            await message.add_reaction("🎟️")

            await asyncio.sleep(timer)

            # Fetch it again
            message = await interaction.channel.fetch_message(message.id)
            reaction = discord.utils.get(message.reactions, emoji="🎟️")

            users = [user async for user in reaction.users() if not user.bot]  # Exclude bots

            # Check
            if len(users) < winners:
                await interaction.followup.send(
                    f"❌ Not enough participants for the raffle! Only {len(users)} people reacted.",
                    ephemeral=True
                )
                return

            winning_users = random.sample(users, winners)

            result_embed = discord.Embed(
                title="🎉 Raffle Winners 🎉",
                description="Here are the lucky winners!",
                color=discord.Color.gold()
            )
            for index, winner in enumerate(winning_users, start=1):
                result_embed.add_field(name=f"Winner #{index}", value=f"🏆 {winner.mention}", inline=False)

            await interaction.followup.send(embed=result_embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(RaffleBasic(bot))
