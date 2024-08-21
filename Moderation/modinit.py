from discord.ext import commands
import discord

moderationSession= False

@commands.command("mod")
async def moderation(ctx):
    global moderationSession
    moderationSession= not moderationSession
    await ctx.send(embed= discord.Embed(
        title= "Moderation Started" if moderationSession else "Moderation Stopped",
        description="Features -",
        color= discord.Color.dark_orange() if moderationSession else  discord.Color.brand_red()
    ))