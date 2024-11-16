import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio

class TicTacToe(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_games = {}

    @app_commands.command(name="TicTacToe", description="Start a game of Tic Tac Toe.")
    async def tik_tac(self, interaction: discord.Interaction, bot_on: bool = False):
        if interaction.channel_id in self.active_games:
            await interaction.response.send_message(
                "A game is already running in this channel. Please finish it or wait for it to end.", ephemeral=True
            )
            return

        self.active_games[interaction.channel_id] = TicTacToeGame(self.bot, interaction.user, bot_on, self)
        await self.active_games[interaction.channel_id].start_game(interaction)

    def end_game(self, channel_id):
        if channel_id in self.active_games:
            del self.active_games[channel_id]


class TicTacToeGame:
    def __init__(self, bot, player1, bot_on, cog):
        self.bot = bot
        self.cog = cog
        self.board = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        self.player1 = player1
        self.player2 = None
        self.bot_on = bot_on
        self.current_turn = None
        self.symbols = {}
        self.winner = None

    async def start_game(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Tic Tac Toe",
            description=f"React with 🏁 to join!\n\n```\n{self.display_board()}\n```\n"
                        f"P1: -\nP2: -",
            color=discord.Color.blue()
        )
        await interaction.response.send_message("Starting Tic Tac Toe game...", ephemeral=True)
        message = await interaction.followup.send(embed=embed)
        await message.add_reaction("🏁")

        def reaction_check(reaction, user):
            return reaction.message.id == message.id and str(reaction.emoji) == "🏁" and user != self.bot.user

        try:
            if self.bot_on:
                reaction, member = await self.bot.wait_for("reaction_add", timeout=30.0, check=reaction_check)
                self.player2 = member
                self.player1 = "Bot"
            else:
                reaction1, member1 = await self.bot.wait_for("reaction_add", timeout=30.0, check=reaction_check)
                reaction2, member2 = await self.bot.wait_for("reaction_add", timeout=30.0, check=reaction_check)
                self.player1, self.player2 = member1, member2

            self.symbols = {self.player1: "X", self.player2: "O"} if random.choice([True, False]) else {self.player1: "O", self.player2: "X"}
            self.current_turn = self.player1 if self.symbols[self.player1] == "X" else self.player2

            embed.description = f"```\n{self.display_board()}\n```\n" \
                                f"P1: {'Bot' if self.player1 == 'Bot' else self.player1.mention} ({self.symbols[self.player1]})\n" \
                                f"P2: {'Bot' if self.player2 == 'Bot' else self.player2.mention} ({self.symbols[self.player2]})\n\n" \
                                f"@{self.current_turn.mention if self.current_turn != 'Bot' else 'Bot'}'s turn now!"
            await message.edit(embed=embed)

            await self.play_game(message, interaction)
        except asyncio.TimeoutError:
            await interaction.channel.send("Game cancelled due to inactivity.")
            self.cog.end_game(interaction.channel_id)

    async def play_game(self, message, interaction):
        while not self.winner and any(pos.isdigit() for pos in self.board):
            current_player = self.current_turn

            if self.bot_on and current_player == "Bot":
                move = self.get_bot_move()
                print(f"Bot chose: {move + 1}")
                await self.make_move(move, message, interaction)
            else:
                def message_check(msg):
                    return msg.author == current_player and msg.content.isdigit() and int(msg.content) in range(1, 10)

                try:
                    msg = await self.bot.wait_for("message", timeout=30.0, check=message_check)
                    move = int(msg.content) - 1
                    print(f"{current_player.mention} chose: {move + 1}")

                    # Check if the chosen position is already filled
                    while self.board[move] in "XO":  # Loop if position is already filled
                        await interaction.channel.send(f"{current_player.mention}, that position is already taken. Please choose a different one!")
                        msg = await self.bot.wait_for("message", timeout=30.0, check=message_check)
                        move = int(msg.content) - 1
                        print(f"{current_player.mention} chose: {move + 1}")

                    await self.make_move(move, message, interaction)

                except asyncio.TimeoutError:
                    await interaction.channel.send(f"{current_player.mention} took too long to respond. Game over!")
                    self.cog.end_game(interaction.channel_id)
                    return

            # Update the winner after the move
            self.winner = self.check_winner()

            # Switch turn only if there's no winner yet
            if not self.winner:
                self.current_turn = self.player1 if self.current_turn == self.player2 else self.player2

        await self.end_game(interaction, message)



    async def make_move(self, position, message, interaction):
        if self.board[position] in "XO":
            return
        
        # Update the board with the current player's move
        self.board[position] = self.symbols[self.current_turn]
        
        # Determine the next turn for display
        next_turn = self.player1 if self.current_turn == self.player2 else self.player2

        embed = discord.Embed(
            title="Tic Tac Toe",
            description=f"```\n{self.display_board()}\n```\n"
                        f"It's @{next_turn.mention if next_turn != 'Bot' else 'Bot'}'s turn now!",
            color=discord.Color.blue()
        )
        await message.edit(embed=embed)



    async def end_game(self, interaction, message):
        if self.winner:
            winner = self.player1 if self.winner == self.symbols[self.player1] else self.player2
            winner_mention = winner.mention if isinstance(winner, discord.User) else winner  # Check if winner is a bot or user
            result = f"🎉 {winner_mention} wins!"
        else:
            result = "It's a draw!"

        embed = discord.Embed(
            title="Game Over",
            description=f"```\n{self.display_board()}\n```\n{result}",
            color=discord.Color.green()
        )
        await message.edit(embed=embed)
        self.cog.end_game(interaction.channel_id)


    def display_board(self):
        return "\n".join([
            f"{self.board[0]} | {self.board[1]} | {self.board[2]}",
            "--+---+--",
            f"{self.board[3]} | {self.board[4]} | {self.board[5]}",
            "--+---+--",
            f"{self.board[6]} | {self.board[7]} | {self.board[8]}"
        ])

    def get_bot_move(self):
        return random.choice([i for i, pos in enumerate(self.board) if pos.isdigit()])

    def check_winner(self):
        win_conditions = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        for a, b, c in win_conditions:
            if self.board[a] == self.board[b] == self.board[c] and self.board[a] in "XO":
                return self.board[a]
        return None


async def setup(bot: commands.Bot):
    await bot.add_cog(TicTacToe(bot))
