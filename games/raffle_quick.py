import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio

class RaffleBasic(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.raffle_group = bot.tree.get_command('raffle') or app_commands.Group(name='raffle', description='Raffle related commands')
        self.add_raffle_basic()

    def add_raffle_basic(self):
        @self.raffle_group.command(
            name="basic", 
            description="Start a basic raffle.")
        @app_commands.describe(
            members="Enter the list of members (comma-separated by ID or mention)",
            winners="Number of winners to pick",
            timer="Time in seconds before raffle starts")
        async def basic_raffle(interaction: discord.Interaction, members: str, winners: int, timer: int):
            member_ids = [m.strip() for m in members.split(',') if m.strip()]
            
            member_list = []
            for member_id in member_ids:

                member_id = member_id.replace("<@!", "").replace("<@", "").replace(">", "")
             
                try:#validate
                    member = await interaction.guild.fetch_member(int(member_id))
                    if member:  
                        member_list.append(member.display_name)
                except (ValueError, discord.NotFound):
                    continue  

            # if enough members 
            if len(member_list) < winners:
                await interaction.response.send_message(
                    f"❌ Not enough members for the number of winners!", ephemeral=True
                )
                return

            # Confirm start
            await interaction.response.send_message(
                f"🎟️ Raffle will start in {timer} seconds with {len(member_list)} members. Picking {winners} winners...", 
                ephemeral=False
            )
            
            await asyncio.sleep(timer)

            await interaction.delete_original_response();
            
            # Random winners
            winning_members = random.sample(member_list, winners)
            
            embed = discord.Embed(
                title="🎉 Raffle Winners 🎉",
                description=f"Here are the lucky {winners} winner(s):",
                color=discord.Color.green()
            )
            for index, winner in enumerate(winning_members, start=1):
                embed.add_field(name=f"Winner #{index}", value=f"🏆 {winner}", inline=False)
            
            await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(RaffleBasic(bot))
