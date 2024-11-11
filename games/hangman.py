import os
import re
import random
import asyncio
import discord
import requests
from discord.ext import commands
from discord import app_commands
from system.hangman_stages import hangman_stages

# List of categories for quotes
categories = [
    "amazing", "attitude", "best", "courage", "dreams", 
    "food", "forgiveness", "freedom", "friendship", 
    "funny", "happiness", "hope", "humor", "imagination", 
    "inspirational", "life", "success"
]

class Hangman(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.hangman_group = app_commands.Group(name="hangman", description="Start or stop a hangman game with a random quote.")
        self.hangman_group.command(name="start", description="Start the Hangman game.")(self.start_hangman)
        self.hangman_group.command(name="stop", description="Stop the current Hangman game.")(self.stop_hangman)
        bot.tree.add_command(self.hangman_group)
        self.active_game_channel = None  
        self.active_games = {}
        self.scores = {}

    async def start_hangman(self, interaction: discord.Interaction):
        await interaction.response.defer()

        # Check if game is already running
        if self.active_game_channel:
            await interaction.followup.send(
                f"A Hangman game is already running in {self.active_game_channel.mention}. Please stop it or wait for it to end."
            )
            return

        # Set current channel as active channel
        self.active_game_channel = interaction.channel
        category = random.choice(categories)
        api_key = os.getenv("QUOTES_KEY")
        url = f"https://api.api-ninjas.com/v1/quotes?category={category}"
        headers = {"X-Api-Key": api_key}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            quote_data = response.json()
            if quote_data:
                quote = quote_data[0]['quote']
                author = quote_data[0]['author']
                words = quote.split()

                def mask_word(word):
                    word_match = re.match(r"([a-zA-Z]+)([^a-zA-Z]*)", word)
                    if word_match:
                        base_word = word_match.group(1)
                        punctuation = word_match.group(2) if word_match.group(2) else ""
                        return "-" * len(base_word) + punctuation, base_word.lower()
                    return word, word.lower()

                num_hidden_words = int(len(words) * 0.7)
                hidden_indices = random.sample(range(len(words)), num_hidden_words)

                masked_words = []
                blanks = {}
                for idx, word in enumerate(words):
                    if idx in hidden_indices:
                        masked, clean_word = mask_word(word)
                        masked_words.append(masked)
                        if clean_word not in blanks:
                            blanks[clean_word] = []
                        blanks[clean_word].append(idx)
                    else:
                        masked_words.append(word)

                obscured_quote = ' '.join(masked_words)

                ascii_embed = discord.Embed(
                    title="🔍 Hangman",
                    description=hangman_stages[1],
                    color=discord.Color.red()
                )
                quote_embed = discord.Embed(
                    title="🔍 Decode the Quote",
                    description=obscured_quote,
                    color=discord.Color.blue()
                )
                quote_embed.set_footer(text=f"Category: {category.capitalize()} | Author: {author}")

                game_id = interaction.user.id
                self.active_games[game_id] = {
                    "quote": quote,
                    "masked_words": masked_words,
                    "blanks": blanks,
                    "ascii_embed": ascii_embed,
                    "quote_embed": quote_embed,
                    "ascii_message": None,
                    "quote_message": None,
                    "guessed_words": set()
                }

                self.active_games[game_id]["ascii_message"] = await interaction.followup.send(embed=ascii_embed)
                self.active_games[game_id]["quote_message"] = await interaction.followup.send(embed=quote_embed)
                await self.track_time_and_update_embed(interaction, game_id)
            else:
                await interaction.followup.send("❌ No quotes found in this category. Try again later.")
        else:
            await interaction.followup.send("❌ Error fetching quote. Please check the API or try again later.")

    async def stop_hangman(self, interaction: discord.Interaction):
        """Stop the current hangman game."""
        if self.active_game_channel:
            self.active_game_channel = None
            self.active_games.clear()
            await interaction.response.send_message("🛑 Hangman game has been stopped.")
        else:
            await interaction.response.send_message("❌ No Hangman game is currently running.")

    async def track_time_and_update_embed(self, interaction: discord.Interaction, game_id: int):
        game_data = self.active_games[game_id]
        
        total_dashes = sum(1 for word in game_data["masked_words"] if "-" in word)
        total_time = max(total_dashes * 20, 30)
        interval = total_time / 7

        for stage in range(2, 8):
            await asyncio.sleep(interval)
            if game_id not in self.active_games:
                return

            game_data["current_stage"] = stage
            game_data["ascii_embed"].description = hangman_stages[stage]

            if game_data["ascii_message"]:
                try:
                    await game_data["ascii_message"].delete()
                except discord.errors.NotFound:
                    pass

            if game_data["quote_message"]:
                try:
                    await game_data["quote_message"].delete()
                except discord.errors.NotFound:
                    pass

            game_data["ascii_message"] = await interaction.followup.send(embed=game_data["ascii_embed"])
            game_data["quote_message"] = await interaction.followup.send(embed=game_data["quote_embed"])

        if game_id in self.active_games:
            await interaction.followup.send("⏰ Oops!! Bill got hanged. Game Over.")
            await self.display_scoreboard(interaction)
            del self.active_games[game_id]
            self.active_game_channel = None  # Clear active channel 

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        game_id = message.author.id
        if game_id in self.active_games and len(message.content.split()) == 1:
            guess = message.content.lower()
            game_data = self.active_games[game_id]
            blanks = game_data["blanks"]

            if guess in blanks and guess not in game_data["guessed_words"]:
                game_data["guessed_words"].add(guess)
                indices = blanks[guess]
                for index in indices:
                    game_data["masked_words"][index] = game_data["quote"].split()[index]
                
                updated_quote = ' '.join(game_data["masked_words"])
                game_data["quote_embed"].description = updated_quote

                if game_data["quote_message"]:
                    try:
                        await game_data["quote_message"].edit(embed=game_data["quote_embed"])
                    except discord.errors.NotFound:
                        pass

                if message.author.id not in self.scores:
                    self.scores[message.author.id] = 0
                self.scores[message.author.id] += 1  # Add points 
                
                del blanks[guess]
                if not blanks:
                    await message.channel.send("🎉 Congratulations! You saved Bill!")
                    await self.display_scoreboard(message.channel)
                    del self.active_games[game_id]
                    self.active_game_channel = None  # Clear active channel 

    async def display_scoreboard(self, interaction_or_channel):
        scoreboard = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        scoreboard_text = "\n".join(
            [f"<@{user_id}>: {score} points" for user_id, score in scoreboard]
        )
        embed = discord.Embed(
            title="🏆 Scoreboard",
            description=scoreboard_text if scoreboard_text else "No scores yet!",
            color=discord.Color.gold()
        )
        if isinstance(interaction_or_channel, discord.Interaction):
            await interaction_or_channel.followup.send(embed=embed)
        else:
            await interaction_or_channel.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Hangman(bot))


