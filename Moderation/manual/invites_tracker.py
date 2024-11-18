import discord
from discord import app_commands
from discord.ext import commands
from collections import defaultdict


class InviteTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tracking = False
        self.invite_data = defaultdict(int)  # Tracks invites 
        self.initial_invites = {}

    invite_commands_group = app_commands.Group(name="invites", description="Manage invite tracking.")

    @invite_commands_group.command(name="tracker", description="Start tracking invites.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def start_tracking(self, interaction: discord.Interaction):
        if self.tracking:
            await interaction.response.send_message("Invite tracking is already active.", ephemeral=True)
            return

        self.tracking = True
        self.invite_data.clear() 
        self.initial_invites.clear()
        await interaction.response.send_message("Invite tracking has started.", ephemeral=True)

        guild = interaction.guild
        invites = await guild.invites()

        self.initial_invites = {invite.code: invite.uses for invite in invites if invite.inviter}

        # print("Tracking started. Initial invites:", self.initial_invites)

    @invite_commands_group.command(name="leaderboard", description="Show the current invite leaderboard.")
    async def show_leaderboard(self, interaction: discord.Interaction):
        if not self.tracking:
            await interaction.response.send_message("🚫 Invite tracking is not active.", ephemeral=True)
            return

        if not self.invite_data:
            await interaction.response.send_message("📭 No invites have been tracked yet!", ephemeral=True)
            return

        # Sort
        sorted_leaderboard = sorted(self.invite_data.items(), key=lambda x: x[1], reverse=True)
        leaderboard_text = "\n".join(
            [
                f"🥇 <@{user_id}>: {invites} invite(s)" if i == 0 else
                f"🥈 <@{user_id}>: {invites} invite(s)" if i == 1 else
                f"🥉 <@{user_id}>: {invites} invite(s)" if i == 2 else
                f"⭐ <@{user_id}>: {invites} invite(s)"
                for i, (user_id, invites) in enumerate(sorted_leaderboard[:10])
            ]
        )

        embed = discord.Embed(
            title="🌟 Invite Leaderboard 🌟",
            description=leaderboard_text or "No invites to display.",
            color=discord.Color.blue(),
        )
        embed.set_footer(text="Keep inviting friends to climb the leaderboard! 🚀")

        await interaction.response.send_message(embed=embed)

    @invite_commands_group.command(name="stop", description="Stop tracking invites.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def stop_tracking(self, interaction: discord.Interaction):
        if not self.tracking:
            await interaction.response.send_message("Invite tracking is not active.", ephemeral=True)
            return

        self.tracking = False
        self.invite_data.clear()
        self.initial_invites.clear()
        await interaction.response.send_message("Invite tracking has been stopped.", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Listener for when a new member joins to update the invite counts."""
        if not self.tracking:
            return

        guild = member.guild
        current_invites = await guild.invites()
        matched = False

        for invite in current_invites:
            if invite.code in self.initial_invites:
                if invite.uses > self.initial_invites[invite.code]:
                    inviter_id = invite.inviter.id if invite.inviter else None
                    if inviter_id:
                        self.invite_data[inviter_id] += 1
                        self.initial_invites[invite.code] = invite.uses
                        # print(f"Updated invite count for {inviter_id}: {self.invite_data[inviter_id]}")
                        matched = True
                    else:
                        print(f"Invite {invite.code} used, but inviter not found.")
                    break

        # if not matched:
        #     print(f"No matching invite found for new member: {member.name}")


async def setup(bot: commands.Bot):
    await bot.add_cog(InviteTracker(bot))
