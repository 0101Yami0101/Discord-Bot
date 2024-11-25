import discord
from discord.ext import commands
from discord import app_commands

class WelcomeGoodbyeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_message = None

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        if self.welcome_message:
            try:
                embed = discord.Embed(
                    title="🎉 Welcome to the Server! 🎉",
                    description=self.welcome_message.replace("{user}", member.mention),
                    color=discord.Color.blue()
                )
                embed.set_footer(text="Enjoy your stay! 🌟")
                await member.send(embed=embed)
            except discord.DiscordException as e:
                print(f"Failed to send DM to {member.name}: {e}")

    @app_commands.command(name="welcome", description="Set the welcome message for new members.")
    async def set_welcome_message(self, interaction: discord.Interaction, message: str):

        self.welcome_message = message
        await interaction.response.send_message(
            f"Welcome message has been set to:\n\n`{message}`",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(WelcomeGoodbyeCog(bot))
